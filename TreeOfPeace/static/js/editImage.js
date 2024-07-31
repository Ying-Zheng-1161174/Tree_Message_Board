document.addEventListener("DOMContentLoaded", function () {
  const profileImageInput = document.getElementById("profile_image_input");
  const removeImageButton = document.getElementById("remove_image_button");
  const addImageButton = document.getElementById("add_image_button");

  // Handle profile image change, upload an new image
  if (profileImageInput) {
    profileImageInput.addEventListener("change", loadFile);
  }

  // Handle profile image remove
  if (removeImageButton) {
    removeImageButton.addEventListener("click", removeImage);
  }

  // Handle profile image add
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
    image.className = "img-thumbnail mb-2";
    if (imageWrapper) {
      imageWrapper.insertBefore(image, imageWrapper.firstChild);
    }

    // Create buttons if not exist
    if (!imageButtons) {
      const buttonsDiv = document.createElement("div");
      buttonsDiv.id = "image_buttons";
      buttonsDiv.innerHTML = `
          <button type="button" class="btn btn-sm btn-secondary" onclick="document.getElementById('profile_image_input').click();">Change picture</button>
          <button type="button" id="remove_image_button" class="btn btn-sm btn-danger bg-opacity-50">Delete</button>`;
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
    // Hide "Add image" button when new image uploaded
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
    image.remove(); // Hide image when it been deleted
  }

  if (imageButtons) {
    imageButtons.remove();
  }

  if (imageInput) {
    imageInput.value = ""; // Clear file input
  }

  // Create the 'Add Image' button when the profile image is deleted
  let addImageButton = document.getElementById("add_image_button");
  if (!addImageButton) {
    addImageButton = document.createElement("button");
    addImageButton.type = "button";
    addImageButton.id = "add_image_button";
    addImageButton.className = "btn btn-sm btn-secondary";
    addImageButton.textContent = "Add image";
    addImageButton.onclick = function () {
      document.getElementById("profile_image_input").click();
    };
    profileImageWrapper.appendChild(addImageButton);
  }
  // Display "Add image" button
  addImageButton.style.display = "block";

  document.getElementById("remove_image").value = "true";
}
