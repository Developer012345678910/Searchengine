/* Register the service worker */
if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("/service-worker.js");
}

/* Fetch the crawled data and store it in db1 */
let db1 = [];
const searchInput = document.getElementById("search-input"); 
const resultsContainer = document.getElementById("results-container");

fetch("crawled_data.json")
  .then(response => response.json())
  .then(data => {
    db1 = data;
    console.log(db1);

    search("bu"); /* Searching Only !!!!! Works in the fetch Block!!!!!!! */
    searchInput.addEventListener("input", () =>
       { search(searchInput.value.trim());

       });
  });

/* Search Function */
function search(keyword) {
    resultsContainer.innerHTML = ""; // Delete all old results

    for (const website of db1) {

        const url = website[0];
        const description = website[1];

        if (
            url.toLowerCase().includes(keyword.toLowerCase()) ||
            description.toLowerCase().includes(keyword.toLowerCase())
        ) {
            const card = document.createElement("div");
            card.classList.add("card");

            card.innerHTML = `
                <a href="https://${url}" target="_blank">${url}</a><br>
                ${description}
            `;

            resultsContainer.appendChild(card);
        }
    }
}



