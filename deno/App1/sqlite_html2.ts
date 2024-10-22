import { Application, Router, send } from "https://deno.land/x/oak/mod.ts";
import { DB } from "https://deno.land/x/sqlite/mod.ts";

// Initialize SQLite database
const db = new DB("test.db");

// Create table if it doesn't exist
db.execute(`
  CREATE TABLE IF NOT EXISTS people (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT
  )
`);

// Insert some initial data if the table is empty
const peopleCount = [...db.query("SELECT COUNT(*) FROM people")][0][0];
if (peopleCount === 0) {
  for (const name of ["Peter Parker", "Clark Kent", "Bruce Wayne"]) {
    db.query("INSERT INTO people (name) VALUES (?)", [name]);
  }
}

const router = new Router();

// API route to fetch people data as JSON
router.get("/api/people", (ctx) => {
  const people = db.query("SELECT name FROM people");
  const peopleList = people.map(([name]: [string]) => name);

  ctx.response.body = { people: peopleList };
});

const app = new Application();

// Middleware to serve static files
app.use(async (ctx, next) => {
  const filePath = ctx.request.url.pathname;
  if (filePath === "/") {
    await send(ctx, "main2.html", {
      root: `${Deno.cwd()}/static`,
    });
  } else {
    await next();
  }
});

// Use router for API
app.use(router.routes());
app.use(router.allowedMethods());

console.log("Server running on http://localhost:8000");
await app.listen({ port: 8000 });
