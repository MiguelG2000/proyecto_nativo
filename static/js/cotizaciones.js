function filterQuotes() {
    let searchInput = document.getElementById("search").value.toLowerCase();
    let rows = document.querySelectorAll("tbody tr");

    rows.forEach(row => {
        let idCell = row.cells[0]?.textContent.toLowerCase() || "";
        let dateCell = row.cells[1]?.textContent.toLowerCase() || "";

        let matchID = idCell.includes(searchInput);
        let matchDate = dateCell.includes(searchInput);

        if (matchID || matchDate) {
            row.style.display = "";
        } else {
            row.style.display = "none";
        }
    });
}
