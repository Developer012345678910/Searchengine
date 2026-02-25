/* Fetch the crawled data and store it in db1 */
let db1 = {};
const searchInput = document.getElementById("search-input"); 
const resultsContainer = document.getElementById("results-container");

fetch("crawled_data.json")
  .then(response => response.json())
  .then(data => {
    db1 = data;
    console.log("Loaded data:", db1);

    // Perform initial search
    search("");
    
    // Add event listener for real-time search
    searchInput.addEventListener("input", () => {
      search(searchInput.value.trim());
    });
  })
  .catch(error => {
    console.error("Error loading crawled_data.json:", error);
    resultsContainer.innerHTML = "<p>Error loading search data. Please check if crawled_data.json exists.</p>";
  });

/**
 * Search function that filters websites by keyword
 * Works with new data format: { name: {...}, ... }
 */
function search(keyword) {
    resultsContainer.innerHTML = ""; // Clear previous results

    // Convert db1 object values to array if needed
    const websites = Array.isArray(db1) ? db1 : Object.values(db1);

    if (websites.length === 0) {
        resultsContainer.innerHTML = "<p>No websites found. Run the crawler first.</p>";
        return;
    }

    let resultCount = 0;

    for (const website of websites) {
        // Support both old format [name, title] and new format {name, title, ...}
        const name = Array.isArray(website) ? website[0] : website.name || "";
        const title = Array.isArray(website) ? website[1] : website.title || "";

        // Skip if keyword doesn't match
        if (keyword && !name.toLowerCase().includes(keyword.toLowerCase()) && 
            !title.toLowerCase().includes(keyword.toLowerCase())) {
            continue;
        }

        resultCount++;
        const card = document.createElement("div");
        card.classList.add("card");

        // Display metadata if available
        let metadata = "";
        if (!Array.isArray(website) && website.last_crawled) {
            const crawlDate = new Date(website.last_crawled).toLocaleDateString();
            metadata = `<small>Last updated: ${crawlDate}</small>`;
        }

        card.innerHTML = `
            <a href="https://${name}" target="_blank" class="website-link">${name}</a><br>
            <span class="website-title">${title}</span>
            ${metadata}
        `;

        resultsContainer.appendChild(card);
    }

    // Show message if no results found
    if (resultCount === 0 && keyword) {
        resultsContainer.innerHTML = `<p>No results found for "<strong>${keyword}</strong>"</p>`;
    } else if (resultCount === 0) {
        resultsContainer.innerHTML = "<p>No websites available.</p>";
    }
}



