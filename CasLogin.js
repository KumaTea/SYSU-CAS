// ==UserScript==
// @name               中大自动验证码认证
// @name:en            SYSU CAS Auto Captcha Login
// @name:zh            中大自动验证码认证
// @namespace          https://github.com/KumaTea
// @namespace          https://greasyfork.org/en/users/169784-kumatea
// @homepage           https://github.com/KumaTea/SYSU-CAS
// @version            0.1.2.0
// @description        中山大学身份验证系统自动识别验证码登录
// @description:en     Automatic Script for Solving captcha of CAS (Central Authentication Service) of Sun Yat-sen University
// @description:zh     中山大学身份验证系统自动识别验证码登录
// @description:zh-cn  中山大学身份验证系统自动识别验证码登录
// @author             KumaTea
// @match              https://cas.sysu.edu.cn/cas/login*
// @license            MIT
// @require            https://unpkg.com/tesseract.js@v2.1.0/dist/tesseract.min.js
// @require            https://unpkg.com/sweetalert@2.1.2/dist/sweetalert.min.js
// ==/UserScript==


/* jshint esversion: 8 */
// "use strict";

const captcha_regex = /[A-Za-z0-9]/g;
sweetAlert("正在加载识别组件……", {buttons: false, timer: 3000,});
console.log("Fetching: https://tessdata.projectnaptha.com/4.0.0/eng.traineddata.gz")

function react_input(component, value) {
  // Credit: https://github.com/facebook/react/issues/11488#issuecomment-347775628
  let last_value = component.value;
  component.value = value;
  let event = new Event("input", {bubbles: true});
  // React 15
  event.simulated = true;
  // React 16
  let tracker = component._valueTracker;
  if (tracker) {
    tracker.setValue(last_value);
  }
  component.dispatchEvent(event);
}

react_input(document.getElementById("captcha"), "正在加载识别组件，请耐心等待……");

async function solve() {
  if (document.getElementById("captcha")) {
    let result = "";
    while (result.length !== 4) {
        await Tesseract.recognize(document.captchaImg, "eng").then(({ data: { text } }) => {result = text.match(captcha_regex).join("");});
        console.log("Recognized: " + result);
        react_input(document.getElementById("captcha"), result);
    }
    console.log("Submitting: " + result);
    if (!document.querySelector("input.btn.btn-submit.btn-block").disabled) {
      document.querySelector("input.btn.btn-submit.btn-block").click();
    } else {
      console.log("No username!");
      sweetAlert("无用户名", "您尚未输入用户名");
    }
  }
}

solve();
