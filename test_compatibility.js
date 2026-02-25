// Simulate the new data format
const newFormat = {
  "example.com": {
    "name": "example.com",
    "title": "Example Domain",
    "first_crawled": "2026-02-25T15:11:07.745730",
    "last_crawled": "2026-02-25T15:11:07.745730"
  },
  "github.com/user": {
    "name": "github.com/user",
    "title": "GitHub User Profile",
    "first_crawled": "2026-02-25T15:11:07.745736",
    "last_crawled": "2026-02-25T15:11:07.745736"
  }
};

// Simulate the old data format
const oldFormat = [
  ["example.com", "Example Domain"],
  ["github.com/user", "GitHub User Profile"]
];

console.log("Testing new format compatibility...");

// Test with new format
let db1 = newFormat;
const websites = Array.isArray(db1) ? db1 : Object.values(db1);

console.log(`\nNew format: Found ${websites.length} websites`);
websites.forEach(website => {
  const name = Array.isArray(website) ? website[0] : website.name;
  const title = Array.isArray(website) ? website[1] : website.title;
  const lastCrawled = !Array.isArray(website) ? website.last_crawled : "N/A";
  console.log(`  - ${name}: ${title} (Updated: ${lastCrawled})`);
});

// Test with old format
console.log("\nTesting old format compatibility...");
db1 = oldFormat;
const websites2 = Array.isArray(db1) ? db1 : Object.values(db1);

console.log(`Old format: Found ${websites2.length} websites`);
websites2.forEach(website => {
  const name = Array.isArray(website) ? website[0] : website.name;
  const title = Array.isArray(website) ? website[1] : website.title;
  console.log(`  - ${name}: ${title}`);
});

console.log("\nCompatibility test passed!");
