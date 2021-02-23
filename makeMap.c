#include <stdio.h>
#include <stdlib.h>
#include <sqlite3.h>
#include <string.h>

int split(char *string, char sep, int n_char, char ***array_values)
{
	int n_values = 1;
	int start = 0;

	for(int x = 0; x < n_char; x++)
	{
		if(string[x] == sep)
			n_values++;
	}
	*array_values = malloc(n_values * sizeof(char**));

	for(int x = 0; x < n_values; x++)
	{
		for(int y = start; y <= n_char; y++)
		{
			if(string[y] == sep || string[y] == '\0')
			{
				(*array_values)[x] = malloc((y - start + 1) * sizeof(char*));
				for(int z = 0; z < y - start; z++)
					(*array_values)[x][z] = string[z + start];
				(*array_values)[x][y - start] = '\0';
				start = y + 1;
				break;
			}
		}
	}

	return n_values;
}

int main()
{
	char *db_name = "map.db";
	sqlite3 *conn;
	sqlite3_stmt *statement;
	char *errMsg;
	char *query;
	int status;

	query = "CREATE TABLE systems (\
		 id INT NOT NULL PRIMARY KEY,\
		 name TEXT NOT NULL,\
		 x FLOAT NOT NULL,\
		 y FLOAT NOT NULL,\
		 z FLOAT NOT NULL)";
	status = sqlite3_open(db_name, &conn);
	if(status == SQLITE_ERROR)
	{
		printf("Error: %s\n", sqlite3_errmsg(conn));
		return 1;
	}

	// Remember to destroy prepared statements to avoid mem leaks
	status = sqlite3_prepare(conn, query, -1, &statement, NULL);
	if(status == SQLITE_ERROR)
	{
		printf("Error: %s\n", sqlite3_errmsg(conn));
		return 1;
	}

	status = sqlite3_step(statement);
	printf("Return: %d\n", status);

	// This function is used to destroy a prepared statement
	status = sqlite3_finalize(statement);
	if(status == SQLITE_ERROR)
	{
		printf("Error: %s\n", sqlite3_errmsg(conn));
		return 1;
	}

	sqlite3_close(conn);
}
