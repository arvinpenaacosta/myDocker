package main

import (
    "database/sql"
    "fmt"
    "html/template"
    "log"
    "net/http"
    "os"

    _ "github.com/denisenkom/go-mssqldb"
    "github.com/joho/godotenv"
)

var templates = template.Must(template.ParseGlob("templates/*.html"))

var db *sql.DB

// Load environment variables
func loadEnv() {
    err := godotenv.Load()
    if err != nil {
        log.Fatalf("Error loading .env file")
    }
}

// Connect to the database
func getDbConnection() (*sql.DB, error) {
    dbUser := os.Getenv("DB_USER")
    dbPassword := os.Getenv("DB_PASSWORD")
    dbName := os.Getenv("DB_NAME")
    dbHost := os.Getenv("DB_HOST")

    connectionString := fmt.Sprintf("sqlserver://%s:%s@%s?database=%s", dbUser, dbPassword, dbHost, dbName)
    return sql.Open("sqlserver", connectionString)
}

// Render the main page
func indexHandler(w http.ResponseWriter, r *http.Request) {
    distinctWord := os.Getenv("DistinctWord")
    kbPatch := os.Getenv("KBPatch")

    // Query the database
    rows, err := db.Query("SELECT * FROM entries")
    if err != nil {
        log.Fatal(err)
    }
    defer rows.Close()

    var entries []struct {
        Field1 string
        Field2 string
    }

    for rows.Next() {
        var field1, field2 string
        if err := rows.Scan(&field1, &field2); err != nil {
            log.Fatal(err)
        }
        entries = append(entries, struct {
            Field1 string
            Field2 string
        }{field1, field2})
    }

    // Render the template
    err = templates.ExecuteTemplate(w, "indexgo.html", map[string]interface{}{
        "DistinctWord": distinctWord,
        "KBPatch":      kbPatch,
        "Entries":      entries,
    })
    if err != nil {
        http.Error(w, err.Error(), http.StatusInternalServerError)
    }
}

// Handle form submissions
func submitHandler(w http.ResponseWriter, r *http.Request) {
    if r.Method != http.MethodPost {
        http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
        return
    }

    field1 := r.FormValue("field1")
    field2 := r.FormValue("field2")

    // Insert into the database
    _, err := db.Exec("INSERT INTO entries (field1, field2) VALUES (@p1, @p2)", field1, field2)
    if err != nil {
        log.Fatal(err)
    }

    // Redirect to the main page
    http.Redirect(w, r, "/", http.StatusFound)
}

func main() {
    loadEnv()

    // Connect to the database
    var err error
    db, err = getDbConnection()
    if err != nil {
        log.Fatal("Failed to connect to database:", err)
    }
    defer db.Close()

    // Set up the routes
    http.HandleFunc("/", indexHandler)
    http.HandleFunc("/api/submit", submitHandler)
    http.Handle("/statics/", http.StripPrefix("/statics/", http.FileServer(http.Dir("statics"))))

    certDir := "certs"
    sslKeyfile := fmt.Sprintf("%s/server_unencrypted.key", certDir)
    sslCertfile := fmt.Sprintf("%s/server.crt", certDir)

    // Start the HTTPS server
    log.Println("Starting server on :8857")
    err = http.ListenAndServeTLS(":8857", sslCertfile, sslKeyfile, nil)
    if err != nil {
        log.Fatal("ListenAndServeTLS failed:", err)
    }
}
