// 🔄 Send selected action (choice) to backend via POST request
async function sendAction(choice) {
  const res = await fetch('/action', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ choice })  // Sending the selected choice as JSON
  });

  const data = await res.json();  // Wait for response and parse it
  document.getElementById('responseMsg').innerText = data.msg;  // Show message on the page
}

// 🔁 Function to switch between form steps (Step 1 to 5)
function goToStep(step) {
  // Hide all step divs
  ["step1", "step2", "step3", "step4", "step5"].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.classList.add("hidden");
  });

  // Show only the target step
  const target = document.getElementById("step" + step);
  if (target) target.classList.remove("hidden");
}

// ➕ Dynamically add a new slot row in manual form
function addSlot() {
  const container = document.getElementById('manual-slots');

  // Create a wrapper div with form fields
  const div = document.createElement('div');
  div.className = 'grid grid-cols-1 sm:grid-cols-4 gap-2 bg-purple-50 border border-purple-200 p-2 rounded-md relative shadow-sm mt-2 text-xs';

  // Set inner HTML content for new slot (Start, End, Email, Timezone)
  div.innerHTML = `
    <!-- ❌ Button to remove slot -->
    <button type="button" onclick="this.parentNode.remove()" class="absolute top-1 right-2 text-gray-400 hover:text-red-500 text-base font-bold">×</button>

    <!-- ⏰ Start Time -->
    <div>
      <label class="text-xs font-medium text-gray-700">Start</label>
      <input type="datetime-local" name="start_times[]" required class="w-full border border-gray-300 rounded px-2 py-1">
    </div>

    <!-- ⏰ End Time -->
    <div>
      <label class="text-xs font-medium text-gray-700">End</label>
      <input type="datetime-local" name="end_times[]" required class="w-full border border-gray-300 rounded px-2 py-1">
    </div>

    <!-- 📧 Email Address -->
    <div>
      <label class="text-xs font-medium text-gray-700">Email</label>
      <input type="email" name="manual_emails[]" placeholder="you@example.com" required class="w-full border border-gray-300 rounded px-2 py-1">
    </div>

    <!-- 🌍 Timezone Selection -->
    <div>
      <label class="text-xs font-medium text-gray-700">Timezone</label>
      <select name="timezones[]" required class="w-full border border-gray-300 rounded px-2 py-1">
        <option value="Asia/Kolkata">India (Asia/Kolkata)</option>
        <option value="America/New_York">US East (America/New_York)</option>
        <option value="America/Los_Angeles">US West (America/Los_Angeles)</option>
        <option value="Europe/London">UK (Europe/London)</option>
        <option value="Europe/Paris">France (Europe/Paris)</option>
        <option value="Asia/Tokyo">Japan (Asia/Tokyo)</option>
        <option value="Australia/Sydney">Australia (Australia/Sydney)</option>
        <!-- You can add more timezones here -->
      </select>
    </div>
  `;

  // Add the newly created slot block to the container
  container.appendChild(div);
}

// 📄 Show uploaded file name after selecting file
function showFileName(input) {
  const fileNameDisplay = document.getElementById('file-name');
  if (input.files.length > 0) {
    fileNameDisplay.textContent = `Selected: ${input.files[0].name}`; // Show file name
    fileNameDisplay.classList.remove('hidden');
  } else {
    fileNameDisplay.classList.add('hidden'); // Hide if no file selected
  }
}

// ✅ Automatically add one slot input block when page loads (for manual form)
document.addEventListener("DOMContentLoaded", () => {
  if (document.getElementById("manual-slots")) {
    addSlot();  // Add one slot by default
  }
});
