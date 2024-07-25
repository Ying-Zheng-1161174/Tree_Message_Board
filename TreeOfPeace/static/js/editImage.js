document.addEventListener("DOMContentLoaded", function () {
  const profileImageInput = document.getElementById("profile_image_input");
  const removeImageButton = document.getElementById("remove_image_button");
  const addImageButton = document.getElementById("add_image_button");

  if (profileImageInput) {
    profileImageInput.addEventListener("change", loadFile);
  }

  if (removeImageButton) {
    removeImageButton.addEventListener("click", removeImage);
  }

  if (addImageButton) {
    addImageButton.addEventListener("click", function () {
      profileImageInput.click();
    });
  }
});

function loadFile(event) {
  let image = document.getElementById("profile_image");
  const imageWrapper = document.getElementById("profile_image_wrapper");
  const imageButtons = document.getElementById("image_buttons");
  const addImageButton = document.getElementById("add_image_button");

  // If no img tag, create one
  if (!image) {
    image = document.createElement("img");
    image.id = "profile_image";
    image.width = 100;
    image.height = 100;
    if (imageWrapper) {
      imageWrapper.insertBefore(image, imageWrapper.firstChild);
    }

    // Create buttons if not exist
    if (!imageButtons) {
      const buttonsDiv = document.createElement("div");
      buttonsDiv.id = "image_buttons";
      buttonsDiv.innerHTML = `
          <button type="button" onclick="document.getElementById('profile_image_input').click();">Change picture</button>
          <button type="button" id="remove_image_button">Delete</button>`;
      imageWrapper.appendChild(buttonsDiv);

      // Attach event listener to new created button
      const newRemoveImageButton = document.getElementById(
        "remove_image_button"
      );
      if (newRemoveImageButton) {
        newRemoveImageButton.addEventListener("click", removeImage);
      }
    }
  }

  if (addImageButton) {
    // Hide "Add image" button
    addImageButton.style.display = "none";
  }

  if (event.target.files && event.target.files[0]) {
    image.src = URL.createObjectURL(event.target.files[0]);
    image.onload = function () {
      URL.revokeObjectURL(image.src); // free memory
    };
  }
}

function removeImage() {
  const image = document.getElementById("profile_image");
  const imageInput = document.getElementById("profile_image_input");
  const profileImageWrapper = document.getElementById("profile_image_wrapper");
  const imageButtons = document.getElementById("image_buttons");

  if (image) {
    image.remove();
    // image.style.display = "none"; // Hide image
  }

  if (imageButtons) {
    imageButtons.remove();
  }

  if (imageInput) {
    imageInput.value = ""; // Clear file input
  }

  let addImageButton = document.getElementById("add_image_button");
  if (!addImageButton) {
    addImageButton = document.createElement("button");
    addImageButton.type = "button";
    addImageButton.id = "add_image_button";
    addImageButton.textContent = "Add image";
    addImageButton.onclick = function () {
      document.getElementById("profile_image_input").click();
    };
    profileImageWrapper.appendChild(addImageButton);
  }
  // Show "Add image" button
  addImageButton.style.display = "block";

  document.getElementById("remove_image").value = "true";
}
