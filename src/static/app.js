document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to handle participant deletion
  async function handleDeleteParticipant(event) {
    const button = event.target;
    const activity = button.dataset.activity;
    const email = button.dataset.email;

    if (!confirm(`Are you sure you want to remove ${email} from ${activity}?`)) {
      return;
    }

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/participants/${encodeURIComponent(email)}`,
        {
          method: "DELETE",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        messageDiv.classList.remove("hidden");

        // Refresh activities list
        await fetchActivities();

        // Hide message after 5 seconds
        setTimeout(() => {
          messageDiv.classList.add("hidden");
        }, 5000);
      } else {
        messageDiv.textContent = result.detail || "Failed to remove participant";
        messageDiv.className = "error";
        messageDiv.classList.remove("hidden");
      }
    } catch (error) {
      messageDiv.textContent = "Failed to remove participant. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error removing participant:", error);
    }
  }

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        // Build participants list
        let participantsList = "";
        if (details.participants.length > 0) {
          participantsList = `
            <div class="participants-section">
              <strong>Participants:</strong>
              <ul class="participants-list">
                ${details.participants.map(email => `
                  <li>
                    <span class="participant-email">${email}</span>
                    <button class="delete-btn" data-activity="${name}" data-email="${email}" title="Remove participant">
                      🗑️
                    </button>
                  </li>
                `).join('')}
              </ul>
            </div>
          `;
        } else {
          participantsList = `
            <div class="participants-section">
              <strong>Participants:</strong>
              <p class="no-participants">No participants yet. Be the first to sign up!</p>
            </div>
          `;
        }

        // Build availability section with visual indicator
        let availabilitySection = '';
        if (spotsLeft === 0) {
          availabilitySection = `
            <p class="availability-full">
              <strong>Availability:</strong> 
              <span class="full-badge">🔴 FULL - No spots available</span>
            </p>
          `;
        } else if (spotsLeft === 1) {
          availabilitySection = `
            <p class="availability-low">
              <strong>Availability:</strong> 
              <span class="low-badge">⚠️ Only 1 spot left!</span>
            </p>
          `;
        } else {
          availabilitySection = `
            <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          `;
        }

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          ${availabilitySection}
          ${participantsList}
        `;

        // Add visual class if activity is full
        if (spotsLeft === 0) {
          activityCard.classList.add('activity-full');
        }

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown only if spots are available
        const spotsAvailable = details.max_participants - details.participants.length;
        if (spotsAvailable > 0) {
          const option = document.createElement("option");
          option.value = name;
          option.textContent = name;
          activitySelect.appendChild(option);
        }
      });

      // Add event listeners for delete buttons
      document.querySelectorAll(".delete-btn").forEach(button => {
        button.addEventListener("click", handleDeleteParticipant);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        
        // Refresh activities list to show new participant
        await fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Handle check my activities form submission
  const checkActivitiesForm = document.getElementById("check-activities-form");
  checkActivitiesForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("check-email").value;
    const myActivitiesList = document.getElementById("my-activities-list");

    try {
      const response = await fetch(
        `/my-activities?email=${encodeURIComponent(email)}`
      );

      const result = await response.json();

      if (response.ok) {
        const activityCount = Object.keys(result).length;
        
        if (activityCount === 0) {
          myActivitiesList.innerHTML = `
            <p class="no-activities">You are not registered for any activities yet.</p>
          `;
        } else {
          myActivitiesList.innerHTML = `
            <p class="activities-count">You are registered for ${activityCount} ${activityCount === 1 ? 'activity' : 'activities'}:</p>
            <div class="my-activities-grid">
              ${Object.entries(result).map(([name, details]) => `
                <div class="my-activity-card">
                  <h4>${name}</h4>
                  <p>${details.description}</p>
                  <p><strong>Schedule:</strong> ${details.schedule}</p>
                </div>
              `).join('')}
            </div>
          `;
        }
        
        myActivitiesList.classList.remove("hidden");
      } else {
        myActivitiesList.innerHTML = `<p class="error">Error: ${result.detail || "Failed to load activities"}</p>`;
        myActivitiesList.classList.remove("hidden");
      }
    } catch (error) {
      myActivitiesList.innerHTML = `<p class="error">Failed to load your activities. Please try again.</p>`;
      myActivitiesList.classList.remove("hidden");
      console.error("Error fetching my activities:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
