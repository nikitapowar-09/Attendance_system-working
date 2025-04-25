const calendarGrid = document.getElementById("calendar-grid");
const monthYearDisplay = document.getElementById("month-year");
const prevMonthBtn = document.getElementById("prev-month");
const nextMonthBtn = document.getElementById("next-month");
const markLeaveBtn = document.getElementById("mark-leave");
const cancelLeaveBtn = document.getElementById("cancel-leave");

let currentDate = new Date();
let attendance = {};
let selectedDate = null;

// Government holidays (YYYY-MM-DD format)
const governmentHolidays = [
  "2025-01-01", // New Year's Day
  "2025-08-15", // Independence Day
  "2025-10-02", // Gandhi Jayanti
  "2024-12-25"  // Christmas
];

function renderCalendar(date) {
  const year = date.getFullYear();
  const month = date.getMonth();
  monthYearDisplay.textContent = `${date.toLocaleString("default", { month: "long" })} ${year}`;

  // Create a table structure for the calendar
  const table = document.createElement("table");
  const headerRow = document.createElement("tr");
  const weekdays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  
  // Add weekday headers
  weekdays.forEach(day => {
    const th = document.createElement("th");
    th.textContent = day;
    headerRow.appendChild(th);
  });
  table.appendChild(headerRow);

  const firstDay = new Date(year, month, 1).getDay();
  const lastDate = new Date(year, month + 1, 0).getDate();

  let currentRow = document.createElement("tr");

  // Add empty cells for days before the first day of the month
  for (let i = 0; i < firstDay; i++) {
    const emptyCell = document.createElement("td");
    currentRow.appendChild(emptyCell);
  }

  // Generate day cells for the month
  for (let day = 1; day <= lastDate; day++) {
    const dayCell = document.createElement("td");
    dayCell.classList.add("calendar-day");
    dayCell.textContent = day;

    const dateString = `${year}-${String(month + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`;

    // Mark government holidays
    if (governmentHolidays.includes(dateString)) {
      dayCell.classList.add("holiday");
      dayCell.title = "Government Holiday";
    }

    // Mark weekends (Saturday and Sunday)
    const weekDay = new Date(year, month, day).getDay();
    if (weekDay === 0) { // Sunday
      dayCell.classList.add("holiday");
      dayCell.title = "Sunday (Holiday)";
    } else if (weekDay === 6) { // Saturday
      dayCell.classList.add("holiday");
      dayCell.title = "Saturday (Holiday)";
    }

    // Check attendance and apply appropriate class
    const attendanceKey = `${year}-${month + 1}-${day}`;
    if (attendance[attendanceKey]) {
      dayCell.classList.add(attendance[attendanceKey]);
    }

    // Add click event for selecting a day
    dayCell.addEventListener("click", () => selectDay(dateString, dayCell));

    currentRow.appendChild(dayCell);

    // If the week is complete, add the row to the table
    if (weekDay === 6) {
      table.appendChild(currentRow);
      currentRow = document.createElement("tr");
    }
  }

  // Append the last row if the month ends before Saturday
  if (currentRow.children.length > 0) {
    table.appendChild(currentRow);
  }

  // Clear the grid and append the table
  calendarGrid.innerHTML = "";
  calendarGrid.appendChild(table);
}

function selectDay(dateString, dayCell) {
  selectedDate = dateString; // Store the selected date
  // Remove selection from any previously selected date
  const previouslySelected = document.querySelector(".selected");
  if (previouslySelected) {
    previouslySelected.classList.remove("selected");
  }
  // Add "selected" class to the currently selected day
  dayCell.classList.add("selected");
}

function markLeave() {
  if (selectedDate) {
    // If a date is selected, mark it as leave
    attendance[selectedDate] = "leave";
    updateSelectedCell();
  } else {
    alert("Please select a date first.");
  }
}

function cancelLeave() {
  if (selectedDate) {
    // If a date is selected, cancel the leave
    delete attendance[selectedDate];
    updateSelectedCell();
  } else {
    alert("Please select a date first.");
  }
}

function updateSelectedCell() {
  const selectedCell = document.querySelector(".selected");
  if (selectedCell) {
    const dateString = selectedDate;
    selectedCell.classList.remove("present", "absent", "leave");
    if (attendance[dateString]) {
      selectedCell.classList.add(attendance[dateString]);
    }
  }
}

prevMonthBtn.addEventListener("click", () => {
  currentDate.setMonth(currentDate.getMonth() - 1);
  renderCalendar(currentDate);
});

nextMonthBtn.addEventListener("click", () => {
  currentDate.setMonth(currentDate.getMonth() + 1);
  renderCalendar(currentDate);
});

markLeaveBtn.addEventListener("click", markLeave);
cancelLeaveBtn.addEventListener("click", cancelLeave);

renderCalendar(currentDate);
