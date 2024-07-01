const express = require("express");
const bodyParser = require("body-parser");
const cors = require("cors");
const mysql = require("mysql2");

const app = express();
const port = 3001;

app.use(cors());
app.use(bodyParser.json({ limit: "50mb" }));
app.use(bodyParser.urlencoded({ limit: "50mb", extended: true }));

const db = mysql.createConnection({
  host: "localhost",
  user: "root",
  password: "1234",
  database: "auth_db",
});

db.connect((err) => {
  if (err) {
    console.error("Error connecting to the database:", err);
    return;
  }
  console.log("Connected to the database.");
});

const createUsersTableQuery = `
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255),
    name VARCHAR(255),
    gender VARCHAR(50),
    birthday DATE,
    password VARCHAR(255),
    token VARCHAR(255),
    orgName VARCHAR(255),
    position VARCHAR(255),
    countryCode VARCHAR(10),
    contact VARCHAR(20),
    profilepicture TEXT
);
`;

const createLogsTableQuery = `
CREATE TABLE IF NOT EXISTS logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    eventType VARCHAR(100),
    eventDescription TEXT
);
`;

db.query(createUsersTableQuery, (err, result) => {
  if (err) {
    console.error("Error creating users table:", err);
    return;
  }
  console.log("Users table created or already exists.");
});

db.query(createLogsTableQuery, (err, result) => {
  if (err) {
    console.error("Error creating logs table:", err);
    return;
  }
  console.log("Logs table created or already exists.");
});

function logEvent(eventType, eventDescription) {
  const insertLogQuery = `
    INSERT INTO logs (eventType, eventDescription)
    VALUES (?, ?)
  `;
  db.query(insertLogQuery, [eventType, eventDescription], (err, result) => {
    if (err) {
      console.error("Error inserting log:", err);
    }
  });
}

app.post("/checkUser", (req, res) => {
  const { email } = req.body;
  const checkQuery = "SELECT * FROM users WHERE email = ?";
  db.query(checkQuery, [email], (err, results) => {
    if (err) {
      console.error("Error checking user:", err);
      logEvent("Error", `Error checking user: ${err.message}`);
      return res.status(500).send("Error checking user.");
    }
    if (results.length > 0) {
      logEvent("Info", `User with email ${email} found.`);
      res.json({ exists: true, userInfo: results[0] });
    } else {
      logEvent("Info", `User with email ${email} not found.`);
      res.json({ exists: false });
    }
  });
});

app.post("/storeAuthInfo", (req, res) => {
  const authInfo = req.body;
  const { id, email, name, gender, birthday, password } = authInfo;

  if (!id || !email || !name || !gender || !birthday || !password) {
    console.error("Missing required auth info fields:", authInfo);
    logEvent(
      "Error",
      `Missing required auth info fields: ${JSON.stringify(authInfo)}`
    );
    return res.status(400).send("Missing required auth info fields.");
  }

  const insertQuery = `
    INSERT INTO users (id, email, name, gender, birthday, password)
    VALUES (?, ?, ?, ?, ?, ?)
    ON DUPLICATE KEY UPDATE
    email = VALUES(email),
    name = VALUES(name),
    gender = VALUES(gender),
    birthday = VALUES(birthday),
    password = VALUES(password);
  `;

  db.query(
    insertQuery,
    [id, email, name, gender, birthday, password],
    (err, result) => {
      if (err) {
        console.error("Error storing or updating auth info:", err);
        logEvent(
          "Error",
          `Error storing or updating auth info: ${err.message}`
        );
        return res.status(500).send("Error storing or updating auth info.");
      }
      logEvent(
        "Info",
        `Auth info for user ${email} stored/updated successfully.`
      );
      res.send("Auth info received and stored/updated.");
    }
  );
});
// Assuming you have already set up your MySQL connection and logEvent function as shown previously

app.get("/logs", (req, res) => {
  const fetchLogsQuery =
    "SELECT timestamp, eventType, eventDescription FROM logs ORDER BY timestamp DESC LIMIT 50"; // Adjust query as per your requirement

  db.query(fetchLogsQuery, (err, result) => {
    if (err) {
      console.error("Error fetching logs:", err);
      return res.status(500).send("Error fetching logs.");
    }
    res.json(result);
  });
});

app.post("/updateProfile", (req, res) => {
  const {
    id,
    name,
    email,
    gender,
    birthday,
    password,
    profilepicture,
    countryCode,
    contact,
  } = req.body;

  const updateQuery = `
    UPDATE users 
    SET name = ?,
        email = ?,
        gender = ?,
        birthday = ?,
        password = ?,
        profilepicture = ?,
        countryCode = ?,
        contact = ?
    WHERE id = ?
  `;

  db.query(
    updateQuery,
    [
      name,
      email,
      gender,
      birthday,
      password,
      profilepicture,
      countryCode,
      contact,
      id,
    ],
    (err, result) => {
      if (err) {
        console.error("Error updating profile:", err);
        logEvent(
          "Error",
          `Error updating profile for user ${id}: ${err.message}`
        );
        return res.status(500).send("Error updating profile.");
      }
      logEvent("Info", `Profile updated successfully for user ${id}.`);
      res.send("Profile updated successfully.");
    }
  );
});

app.post("/updateCompanyInfo", (req, res) => {
  const { email, orgName, position } = req.body;

  const updateQuery = `
    UPDATE users 
    SET orgName = ?,
        position = ?
    WHERE email = ?
  `;

  db.query(updateQuery, [orgName, position, email], (err, result) => {
    if (err) {
      console.error("Error updating company info:", err);
      logEvent(
        "Error",
        `Error updating company info for user ${email}: ${err.message}`
      );
      return res.status(500).send("Error updating company info.");
    }
    logEvent("Info", `Company info updated successfully for user ${email}.`);
    res.send("Company info updated successfully.");
  });
});

app.post("/storeToken", (req, res) => {
  const { token, email } = req.body;

  const updateTokenQuery = `
    UPDATE users 
    SET token = ?
    WHERE email = ?
  `;

  db.query(updateTokenQuery, [token, email], (err, result) => {
    if (err) {
      console.error("Error storing token:", err);
      logEvent(
        "Error",
        `Error storing token for user ${email}: ${err.message}`
      );
      return res.status(500).send("Error storing token.");
    }
    logEvent("Info", `Token stored successfully for user ${email}.`);
    res.send("Token stored successfully.");
  });
});

app.get("/fetchToken/:email", (req, res) => {
  const { email } = req.params;
  const fetchTokenQuery = "SELECT token FROM users WHERE email = ?";
  db.query(fetchTokenQuery, [email], (err, result) => {
    if (err) {
      console.error("Error fetching token:", err);
      logEvent(
        "Error",
        `Error fetching token for user ${email}: ${err.message}`
      );
      return res.status(500).send("Error fetching token.");
    }
    if (result.length > 0) {
      logEvent("Info", `Token fetched successfully for user ${email}.`);
      res.json({ token: result[0].token });
    } else {
      logEvent("Info", `Token not found for user ${email}.`);
      res.status(404).send("Token not found.");
    }
  });
});

app.put("/updateToken/:email", (req, res) => {
  const { email } = req.params;
  const { token } = req.body;

  const updateTokenQuery = `
    UPDATE users 
    SET token = ?
    WHERE email = ?
  `;

  db.query(updateTokenQuery, [token, email], (err, result) => {
    if (err) {
      console.error("Error updating token:", err);
      logEvent(
        "Error",
        `Error updating token for user ${email}: ${err.message}`
      );
      return res.status(500).send("Error updating token.");
    }
    logEvent("Info", `Token updated successfully for user ${email}.`);
    res.send("Token updated successfully.");
  });
});

app.get("/fetchCompanyInfo/:email", (req, res) => {
  const email = req.params.email;

  const fetchCompanyQuery =
    "SELECT orgName, position FROM users WHERE email = ?";
  db.query(fetchCompanyQuery, [email], (err, result) => {
    if (err) {
      console.error("Error fetching company info:", err);
      logEvent(
        "Error",
        `Error fetching company info for user ${email}: ${err.message}`
      );
      return res.status(500).json({ error: "Internal server error" });
    }
    if (result.length === 0) {
      logEvent("Info", `Company info not found for user ${email}.`);
      return res.status(404).json({ error: "Company info not found" });
    }

    const companyInfo = {
      orgName: result[0].orgName,
      position: result[0].position,
      // Add other fields if needed
    };

    logEvent("Info", `Company info fetched successfully for user ${email}.`);
    res.status(200).json(companyInfo);
  });
});

app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
