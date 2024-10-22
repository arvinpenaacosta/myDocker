import { Application, Router } from "https://deno.land/x/oak@v17.1.0/mod.ts";
//import { DB } from "https://deno.land/x/sqlite@v3.9.1/mod.ts";
import { DB } from "https://deno.land/x/sqlite/mod.ts";

// Initialize the SQLite database
let db: DB;
try {
  db = new DB("app.db");
  db.execute(`
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      eid TEXT,
      name TEXT,
      pass TEXT
    )
  `);
  console.log("Database initialized successfully");
} catch (error) {
  console.error("Error initializing database:", error);
  Deno.exit(1);
}

const router = new Router();

// API routes
router.get("/api/users", (ctx) => {
  try {
    const users = db.queryEntries("SELECT id, eid, name, pass FROM users");
    console.log("Retrieved users:", users);
    ctx.response.body = { users };
  } catch (error) {
    console.error("Error retrieving users:", error);
    ctx.response.status = 500;
    ctx.response.body = { message: "Internal server error" };
  }
});

router.post("/api/users", async (ctx) => {
  let transactionStarted = false;
  try {
    const body = await ctx.request.body().value;
    console.log("Received body:", body);

    if (typeof body !== 'object' || body === null) {
      ctx.response.status = 400;
      ctx.response.body = { message: "Invalid request body" };
      return;
    }

    const { eid, name, pass } = body as { eid: string; name: string; pass: string };
    
    if (!eid || !name || !pass) {
      ctx.response.status = 400;
      ctx.response.body = { message: "Missing required fields" };
      return;
    }

    console.log("Attempting to insert user:", { eid, name, pass });
    
    db.execute("BEGIN TRANSACTION");
    transactionStarted = true;
    
    db.queryEntries("INSERT INTO users (eid, name, pass) VALUES (?, ?, ?)", [eid, name, pass]);
    
    db.execute("COMMIT");
    console.log("User inserted successfully");
    
    ctx.response.status = 201;
    ctx.response.body = { message: "User created successfully" };
  } catch (error) {
    console.error("Error creating user:", error);
    if (transactionStarted) {
      try {
        db.execute("ROLLBACK");
      } catch (rollbackError) {
        console.error("Error rolling back transaction:", rollbackError);
      }
    }
    ctx.response.status = 500;
    ctx.response.body = { message: "Internal server error" };
  }
});

// ... (keep the PUT and DELETE routes as they were)

const app = new Application();

// Serve static files from the 'static' directory
app.use(async (ctx, next) => {
  try {
    await ctx.send({
      root: `${Deno.cwd()}/static`,
      index: "index.html",
    });
  } catch {
    await next();
  }
});

// Use the router
app.use(router.routes());
app.use(router.allowedMethods());

console.log("Server running on http://localhost:8000");
await app.listen({ port: 8000 });