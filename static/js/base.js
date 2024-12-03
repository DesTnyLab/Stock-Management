// function to get the today date.
function getTodayDate() {
  const today = new Date();
  const options = { year: "numeric", month: "short", day: "2-digit" };
  const formattedDate = today.toLocaleDateString("en-UK", options); // E.g., Dec 01 2024
  return formattedDate;
}

document.querySelector(
  "#today_date"
).innerHTML = `<b> Date:</b> ${getTodayDate()}`;
