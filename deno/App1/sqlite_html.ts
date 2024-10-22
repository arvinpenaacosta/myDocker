import { Application, Router } from "https://deno.land/x/oak/mod.ts";
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

// Render HTML page with the results
router.get("/", (ctx) => {
  const people = db.query("SELECT name FROM people");

  // Generate HTML page
  let html = `
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>People List</title>
      <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid black; padding: 8px; text-align: left; }
      </style>
    </head>
    <body>
      <h1>List of People</h1>
      <table>
        <thead>
          <tr>
            <th>Name</th>
          </tr>
        </thead>
        <tbody>`;

  for (const [name] of people) {
    html += `<tr><td>${name}</td></tr>`;
  }

  html += `
        </tbody>
      </table>
    </body>
    </html>
  `;

  // Set the response body to the generated HTML
  ctx.response.body = html;
});

const app = new Application();

// Use the router
app.use(router.routes());
app.use(router.allowedMethods());

console.log("Server running on http://localhost:8000");
await app.listen({ port: 8000 });
