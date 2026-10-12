import React, { useEffect, useState } from "react";
import axios from "axios";
import "./SchemaExplorer.css";

function SchemaExplorer() {
  const [schema, setSchema] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [expandedTables, setExpandedTables] = useState({});

  useEffect(() => {
    const fetchSchema = async () => {
      try {
        const response = await axios.get(
          "http://127.0.0.1:5000/schema"
        );

        setSchema(response.data);
        setError("");

        const initialExpanded = {};

        response.data.tables.forEach((table) => {
          initialExpanded[table.table_name] = true;
        });

        setExpandedTables(initialExpanded);
      } catch (err) {
        console.error("Schema error:", err);

        setError(
          err.response?.data?.error ||
          err.message ||
          "Unable to load database schema."
        );
      } finally {
        setLoading(false);
      }
    };

    fetchSchema();
  }, []);

  const toggleTable = (tableName) => {
    setExpandedTables((previous) => ({
      ...previous,
      [tableName]: !previous[tableName],
    }));
  };

  if (loading) {
    return (
      <div className="schema-explorer card">
        <h2>🗄️ Database Schema</h2>
        <p className="schema-loading">
          Loading database schema...
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="schema-explorer card">
        <h2>🗄️ Database Schema</h2>

        <p className="schema-error">
          {error}
        </p>
      </div>
    );
  }

  if (!schema || !schema.tables) {
    return (
      <div className="schema-explorer card">
        <h2>🗄️ Database Schema</h2>
        <p>No schema information available.</p>
      </div>
    );
  }

  return (
    <div className="schema-explorer card">
      <div className="schema-header">
        <div>
          <h2>🗄️ Database Schema</h2>

          <p className="schema-database">
            Database: <strong>{schema.database}</strong>
          </p>
        </div>

        <span className="table-count">
          {schema.tables.length} Tables
        </span>
      </div>

      <div className="schema-tables">
        {schema.tables.map((table) => {
          const isExpanded =
            expandedTables[table.table_name];

          return (
            <div
              className="schema-table"
              key={table.table_name}
            >
              <button
                type="button"
                className="schema-table-header"
                onClick={() =>
                  toggleTable(table.table_name)
                }
              >
                <span>
                  {isExpanded ? "▼" : "▶"}{" "}
                  <strong>{table.table_name}</strong>
                </span>

                <span className="column-count">
                  {table.columns.length} columns
                </span>
              </button>

              {isExpanded && (
                <div className="schema-table-content">
                  <div className="schema-columns">
                    {table.columns.map((column) => (
                      <div
                        className="schema-column"
                        key={column.name}
                      >
                        <div className="column-name">
                          {column.primary_key && (
                            <span
                              className="key-icon"
                              title="Primary Key"
                            >
                              🔑
                            </span>
                          )}

                          {!column.primary_key &&
                            table.foreign_keys.some(
                              (fk) =>
                                fk.column === column.name
                            ) && (
                              <span
                                className="key-icon"
                                title="Foreign Key"
                              >
                                🔗
                              </span>
                            )}

                          <span>
                            {column.name}
                          </span>
                        </div>

                        <span className="column-type">
                          {column.type}
                        </span>
                      </div>
                    ))}
                  </div>

                  {table.foreign_keys.length > 0 && (
                    <div className="foreign-keys">
                      <h4>🔗 Relationships</h4>

                      {table.foreign_keys.map(
                        (fk, index) => (
                          <div
                            className="foreign-key"
                            key={`${fk.column}-${index}`}
                          >
                            <strong>
                              {fk.column}
                            </strong>

                            <span>→</span>

                            <span>
                              {fk.referenced_table}.
                              {fk.referenced_column}
                            </span>
                          </div>
                        )
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default SchemaExplorer;