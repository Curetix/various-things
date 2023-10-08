#!/usr/bin/env zx
import { stringify } from "querystring";
import "zx/globals";

async function healthPing(status = "up", msg = "OK", ping = 0) {
    try {
        const query = {
            status,
            msg,
            ping: ping > 0 ? ping : undefined,
        };
        let res = await fetch(`${process.env.HEALTH_PING_URL}?${stringify(query)}`);
        if (res.ok)
            return true;
    }
    catch (e) {
        echo("Health ping failed");
    }
    return false;
}

async function removeFile(path) {
    try {
        await $ `rm -f ${path}`;
    }
    catch (e) {
        echo("Could not remove file", path);
    }
}

async function backup() {
    const timestamp = new Date()
        .toISOString()
        // Many filesystems don't like the colon character, so replace those with dash
        .replaceAll(":", "-")
        // Remove milliseconds from timestamp
        .replace(/(\.\d{3}Z)/g, "Z");
    const dumpFile = `./${timestamp}.dump`;
    const archiveFile = `./${timestamp}.7z`;
    echo("Starting backup");
    // Dump the database into a tar archive
    try {
        await $ `pg_dump --format=custom --compress=0 --file=${dumpFile} -d $POSTGRES_URL`;
        echo("Database dump created");
    }
    catch (e) {
        echo("Database dump failed", e);
        await removeFile(dumpFile);
        return false;
    }
    // Compress the DB dump using 7zip
    try {
        await $ `7zz -y -bso0 -bsp0 a ${archiveFile} ${dumpFile}`;
        echo("Compressed archive");
    }
    catch (e) {
        echo("Could not compress archive", e);
        return false;
    }
    finally {
        await removeFile(dumpFile);
    }
    // Copy the compressed archive to the rclone remote destination
    try {
        await $ `rclone copy ${archiveFile} $RCLONE_DESTINATION`;
        echo("Database dump uploaded to remote");
    }
    catch (e) {
        echo("Upload failed", e);
        return false;
    }
    finally {
        await removeFile(archiveFile);
    }
    return true;
}

function checkEnv() {
    const required = ["POSTGRES_URL", "RCLONE_DESTINATION", "HEALTH_PING_URL"];
    required.forEach((env) => {
        if (!process.env[env]) {
            throw new Error(`The required environment variable ${env} is not set.`);
        }
    });
}

async function main() {
    checkEnv();
    const start = new Date();
    const result = await backup();
    const end = new Date();
    const time = end.getTime() - start.getTime();
    await healthPing(result ? "up" : "down", "OK", time);
    process.exit(result ? 0 : 1);
}

await main();
