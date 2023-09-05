document.addEventListener("DOMContentLoaded", () => {
    const draggables = document.querySelectorAll(".shallow-draggable");
    const containers = document.querySelectorAll(".chips-container.input");
    let graphDetails = [];
  
    let isDragging = false;
    let draggingElement;
    let activeContainer = null;
  
    draggables.forEach((draggable) => {
      draggable.addEventListener("dragstart", (e) => {
        e.dataTransfer.setData("text/plain", draggable.innerText); // Set the data to be dragged
        draggable.classList.add("dragging");
        isDragging = true;
        draggingElement = draggable;
      });
  
      draggable.addEventListener("dragend", () => {
        draggable.classList.remove("dragging");
        isDragging = false;
      });
    });
  
    containers.forEach((container) => {
      container.addEventListener("dragover", function (e) {
        e.preventDefault();
        if (activeContainer !== container) {
          activeContainer = container;
          container.addEventListener("drop", handleDropEvent);
        }
      });
    });
  
    function handleDropEvent(e) {
      e.preventDefault(); // Prevent default to enable drop event
      const container = e.currentTarget;
      const afterElement = getDragAfterElement(container, e.clientY);
      const dragging = document.querySelector(".dragging");
  
      if (isDragging && dragging === draggingElement) {
        const chipValue = e.dataTransfer.getData("text/plain"); // Get the dragged data
        const chip = createChipElement(chipValue);
        if (afterElement == null) {
          container.appendChild(chip);
        } else {
          container.insertBefore(chip, afterElement);
        }
  
        // Update graphDetails and make the POST request
        graphDetails.push({ id: container.id, value: chipValue });
        updateGraphDetailsOnPage(graphDetails);
        saveGraphDetails(graphDetails);
      }
  
      activeContainer = null;
      container.removeEventListener("drop", handleDropEvent);
    }
  
    function handleRemoveChip(e) {
      const removeButton = e.currentTarget;
      const chip = removeButton.closest(".chip");
      const chipValue = chip.querySelector(".chip-text").textContent;
  
      // Find and remove the corresponding chip from the graphDetails array
      graphDetails = graphDetails.filter((detail) => detail.value !== chipValue);
      chip.remove();
  
      // Update graphDetails and make the POST request
      updateGraphDetailsOnPage(graphDetails);
      saveGraphDetails(graphDetails);
    }
  
    function updateGraphDetailsOnPage(graphDetails) {
      // Clear existing graphDetails elements from the DOM
      const graphDetailsContainer = document.getElementById("graphDetailsContainer");
      graphDetailsContainer.innerHTML = "";
  
      // Add updated graphDetails elements to the DOM
      graphDetails.forEach((details) => {
        const detailsElement = document.createElement("div");
        detailsElement.textContent = JSON.stringify(details);
        graphDetailsContainer.appendChild(detailsElement);
      });
  
      // Add event listeners to the remove buttons
      const removeButtons = document.querySelectorAll(".remove-chip");
      removeButtons.forEach((button) => {
        button.removeEventListener("click", handleRemoveChip); // Clean up previous event listeners
        button.addEventListener("click", handleRemoveChip);
      });
  
    }
  
    function saveGraphDetails(graphDetails) {
      // Make the POST request to save graphDetails
      fetch("/graph", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCSRFToken(),
        },
        body: JSON.stringify({ data: graphDetails }),
      })
        .then((response) => response.json())
        .then((data) => {
          // Handle the response data
          if (data.status === "success") {
            // Update the UI with the new graphDetails
            graphDetails = data.graphDetails;
            updateGraphDetailsOnPage(graphDetails);
          }
        })
        .catch((error) => {
          // Handle errors
        });
    }
  
    function getCSRFToken() {
      const csrfCookie = document.cookie
        .split(";")
        .find((cookie) => cookie.trim().startsWith("csrftoken="));
      if (csrfCookie) {
        return csrfCookie.split("=")[1];
      }
      return "";
    }
  
    function createChipElement(text) {
      const chip = document.createElement("div");
      chip.classList.add("chip");
  
      const chipText = document.createElement("span");
      chipText.classList.add("chip-text");
      chipText.textContent = text;
  
      const removeChip = document.createElement("span");
      removeChip.classList.add("remove-chip");
      removeChip.textContent = "×";
      removeChip.addEventListener("click", handleRemoveChip);
  
      chip.appendChild(chipText);
      chip.appendChild(removeChip);
  
      return chip;
    }
  
    function getDragAfterElement(container, y) {
      const draggableElements = [...container.querySelectorAll(".chip")];
  
      return draggableElements.reduce(
        (closest, child) => {
          const box = child.getBoundingClientRect();
          const offset = y - box.top - box.height / 2;
          if (offset < 0 && offset > closest.offset) {
            return { offset: offset, element: child };
          } else {
            return closest;
          }
        },
        { offset: Number.NEGATIVE_INFINITY }
      ).element;
    }
  });
  