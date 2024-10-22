import { Application, Router, send } from "https://deno.land/x/oak/mod.ts";
import { Database, Model, DataTypes } from "https://deno.land/x/denodb/mod.ts";

// Initialize SQLite database
const db = new Database("sqlite:./test.db"); // Updated to use DenoDB

// Define the Person model
class Person extends Model {
  static table = "people";

  static fields = {
    id: { type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true },
    name: { type: DataTypes.STRING },
  };
}

// Sync the model with the database
await db.link([Person]);
await db.sync(); // Create the table if it doesn't exist

// Insert some initial data if the table is empty
const peopleCount = await Person.count();
if (peopleCount === 0) {
  for (const name of ["Peter Parker", "Clark Kent", "Bruce Wayne"]) {
    const person = new Person({ name });
    await person.save();
  }
}

const router = new Router();

// API route to fetch people data as JSON
router.get("/api/people", async (ctx) => {
  const people = await Person.all();
  ctx.response.body = { people: people.map(person => person.name) };
});

// API route to insert a new person
router.post("/api/people", async (ctx) => {
  try {
    const body = ctx.request.body();
    const { name } = await body.value;

    if (!name) {
      ctx.response.status = 400;
      ctx.response.body = { success: false, message: "Name is required." };
      return;
    }

    const person = new Person({ name });
    await person.save(); // Insert into the database

    ctx.response.body = { success: true, message: "Person added successfully." };
  } catch (error) {
    console.error("Error in POST request:", error); // Log the exact error
    ctx.response.body = { success: false, message: "An error occurred." };
  }
});

const app = new Application();

// Middleware to serve static files
app.use(async (ctx, next) => {
  const filePath = ctx.request.url.pathname;
  if (filePath === "/") {
    await send(ctx, "main3.html", {
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
