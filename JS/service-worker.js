self.addEventListener("install", event => {
  event.waitUntil(
    caches.open("crawl_data_cache").then(cache => { /* Create a cache with name  */
      return cache.addAll([
        "/crawled_data.json"
      ]);
    })
  );
});
