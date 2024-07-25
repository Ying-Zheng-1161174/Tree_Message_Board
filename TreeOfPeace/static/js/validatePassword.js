const check = function () {
  const password = document.getElementById("password").value;
  const confirmPassword = document.getElementById("confirm_password").value;
  const oldPassword = document.getElementById("old_password")?.value;
  const messagePassword = document.getElementById("message_password");
  const messageConfirmPassword = document.getElementById(
    "message_confirm_password"
  );

  if (oldPassword !== undefined) {
    if (oldPassword === password) {
      messagePassword.style.color = "red";
      messagePassword.innerHTML =
        "New password cannot be the same as the old password";
    } else {
      messagePassword.innerHTML = "";
    }
  }

  if (password !== "" && confirmPassword !== "") {
    if (password === confirmPassword) {
      messageConfirmPassword.style.color = "green";
      messageConfirmPassword.innerHTML = "Matching";
    } else {
      messageConfirmPassword.style.color = "red";
      messageConfirmPassword.innerHTML = "Not matching";
    }
  } else {
    messageConfirmPassword.innerHTML = "";
  }
};

document.addEventListener("DOMContentLoaded", function () {
  document.getElementById("password").addEventListener("input", check);
  document.getElementById("confirm_password").addEventListener("input", check);
  document.getElementById("old_password")?.addEventListener("input", check);
});
