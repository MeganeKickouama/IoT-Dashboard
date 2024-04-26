$(document).ready(function() 
{
    section.classList.toggle("dark");
});

function turn_on_led() {
    fetch('/turn_on');
    document.getElementById("toggleSwitch").checked = true;
  };
  
  function turn_off_led() {
    fetch('/turn_off');
    document.getElementById("toggleSwitch").checked = false;
  };
  
  function toggle_led() {
    var isChecked = document.getElementById("toggleSwitch").checked;
    if (isChecked) {
      turn_on_led();
      toggleLamp();
    } else {
      turn_off_led();
      toggleLamp();
    }
  };
  function toggleLamp() {
    var lamp = document.getElementById("lamp");
    lamp.classList.toggle("on");
    lamp.classList.toggle("off");
  };