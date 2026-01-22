/* Register the service worker */
if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("/service-worker.js");
}

/* Fetch the crawled data and store it in db1 */
let db1 = [];

fetch("crawled_data.json")
  .then(response => response.json())
  .then(data => {
    db1 = data;
    console.log(db1);

    search("bu"); /* Searching Only !!!!! Works in the fetch Block!!!!!!! */
  });

/* Search Function */
function search(keyword) {
    for (const website of db1) {
        if(website[0].toLowerCase().includes(keyword.toLowerCase()) == true) {
            /* Test if the keyword in the Name of the website */
            console.log(`Name: ${website[0]}`);; /* Print out the name of the website. */
            console.log(`Discription: ${website[1]}`); /* Print out the discription of the website. */
        }
        if(website[1].toLowerCase().includes(keyword.toLowerCase()) == true) {
            /* Test if the keyword in the Discription */
            console.log(`Name: ${website[0]}`);; /* Print out the name of the website. */
            console.log(`Discription: ${website[1]}`); /* Print out the discription of the website. */
        }
    }
}

const searchInput = document.getElementById("search-input");

searchInput.addEventListener("keydown", function (event) {
  if (event.key === "Enter") {
    const query = searchInput.value.trim();

    if (query.length > 0) {
      const url = "https://www.google.com/search?q=" + encodeURIComponent(query);
      window.location.href = url;
    }
  }
});

