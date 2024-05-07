// ==UserScript==
// @name         Humble Bundle key helper
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  Add buttons to reveal all keys on a Humble Bundle purchase page and copy Steam keys for ArchiSteamFarm
// @author       Curetix
// @homepage     https://github.com/curetix/various-things/javascript/humble_bundle_key_helper.user.js
// @updateURL    https://raw.githubusercontent.com/curetix/various-things/main/javascript/humble_bundle_key_helper.user.js
// @downloadURL  https://raw.githubusercontent.com/curetix/various-things/main/javascript/humble_bundle_key_helper.user.js
// @match        https://www.humblebundle.com/downloads?key=*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=humblebundle.com
// @grant        none
// ==/UserScript==

var $ = window.jQuery;

(function() {
    'use strict';

    // Button to reveal all keys
    const revealButton = $("<button>", { class: "js-bulk-download button-v2 blue rectangular-button", css: { width: "100%", height: "50px", marginBottom: "10px" }}).text("Reveal all");
    revealButton.click(() => {
        const fields = $(".keyfield").not('.redeemed')
        for (let i = 0; i < fields.length; i++) {
            fields[i].click()
        }
    });

    function copyKeys(format = "bgr") {
        const steamKeyList = $("h2:contains('Steam') + div.key-list")[0];
        const fields = steamKeyList.querySelectorAll(".key-redeemer");
        let out = "";
        for (let i = 0; i < fields.length; i++) {
            const title = fields[i].querySelector("h4").innerHTML.trim()
            const key = fields[i].querySelector(".keyfield-value").innerHTML.trim()
            if (format === "bgr") {
                out += `${title}  ${key}\n`
            } else if (format === "cmd") {
                 out += `${key} `
            } else {
                console.log("Unknown key format", format);
                alert("Unknown key format")
            }
        }
        console.log(out);
        navigator.clipboard.writeText(out);
    }

    // Button to copy keys in the ASF UI format (one key per line)
    const copyButton = $("<button>", { class: "js-bulk-download button-v2 rectangular-button", css: { width: "100%", height: "40px", marginBottom: "10px" }}).text("Copy keys for ASF UI");
    copyButton.click(() => copyKeys("bgr"));

    // Button to copy keys in the ASF command format (keys separated by whitespace)
    const copyButton2 = $("<button>", { class: "js-bulk-download button-v2 rectangular-button", css: { width: "100%", height: "40px", marginBottom: "20px" }}).text("Copy keys for ASF command line");
    copyButton2.click(() => copyKeys("cmd"));

    // Add buttons to the start of the key list
    $(".key-container").prepend(revealButton, copyButton, copyButton2);
})();