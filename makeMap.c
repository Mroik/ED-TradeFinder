#include <stdio.h>
#include <stdlib.h>
#include <sqlite3.h>
#include <string.h>

// This function will return an array of strings
// which is an array of chars, therefore every
// pointer inside the pointer will have to be
// freed (excuse the poorly written comments)
char **split(char *string, char sep, int n_char, int *n_str)
{
	//TODO Implement
	char **ris;
	int n_str = 1;

	for(int x = 0; x < n_str; x++)
	{
		if(string[x] == sep)
			n_str++;
	}
	ris = (char**)(malloc(sizeof(char**)*n_str));
}

int main()
{
	char *db_name = "test.db";
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
	if(status)
	{
		printf("Error: %s\n", sqlite3_errmsg(conn));
		return 1;
	}

	// Remember to destroy prepared statements to avoid mem leaks
	status = sqlite3_prepare(conn, query, -1, &statement, NULL);
	if(status)
	{
		printf("Error: %s\n", sqlite3_errmsg(conn));
		return 1;
	}

	status = sqlite3_step(statement);
	printf("Return: %d\n", status);

	// This function is used to destroy a prepared statement
	status = sqlite3_finalize(statement);
	if(status)
	{
		printf("Error: %s\n", sqlite3_errmsg(conn));
		return 1;
	}

	sqlite3_close(conn);
}
