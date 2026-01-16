const db1 = [
    ["GitHub.com", "Where the word builds software"],
    ["YouTube.com", "Youtube, das Video Portal."]
];
 
function search(keyword) {
    for (const website of db1) {
        if(website[0].toLowerCase().includes(keyword.toLowerCase()) == true || website[1].toLowerCase().includes(keyword.toLowerCase()) == true) {
            console.log(website[0]);
        }
    }
}

search("Portal");
