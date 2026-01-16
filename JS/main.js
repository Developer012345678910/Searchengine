/* Add a json db to the Programm (loading) */
const db1 = [
    ["GitHub.com", "Where the word builds software"],
    ["YouTube.com", "Youtube, das Video Portal."]
];
 
function search(keyword) {
    for (const website of db1) {
        if(website[0].toLowerCase().includes(keyword.toLowerCase()) == true) {
            /* Test if the keyword in the Name of the website */
            console.log(website[0]); /* Print out the Name of the Website. */
            console.log(website[1]); /* Print out the discription of the website. */
        }
        if(website[1].toLowerCase().includes(keyword.toLowerCase()) == true) {
            /* Test if the keyword in the Discription */
            console.log(website[0]); /* Print out the name of the website. */
            console.log(website[1]); /* Print out the discription of the website. */
        }
    }
}

search("Portal");
