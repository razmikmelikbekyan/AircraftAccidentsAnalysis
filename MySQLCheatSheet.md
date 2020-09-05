Structured Query Language (SQL)
Structured Query Language is a standard Database language which is used to create, maintain and retrieve the relational database. Following are some interesting facts about SQL.

- SQL is case insensitive. But it is a recommended practice to use keywords (like SELECT, UPDATE
, CREATE, etc) in capital letters and use user defined things (liked table name, column name, etc) in small letters.
- We can write comments in SQL using “–” (double hyphen) at the beginning of any line.
- SQL is the programming language for relational databases (explained below) like MySQL, Oracle
, Sybase, SQL Server, Postgre, etc. Other non-relational databases (also called NoSQL) databases like MongoDB, DynamoDB, etc do not use SQL
- Although there is an ISO standard for SQL, most of the implementations slightly vary in syntax
. So we may encounter queries that work in SQL Server but do not work in MySQL.


### Cheat sheet

#### Basic staff: https://www.geeksforgeeks.org/structured-query-language/
* login:
    
    `mysql -u USERNAME -p`

* see the list of databases:
    
    `show databases;`

* use the database: 
    
    `use DBNAME;`

* copy db in the same mysql client: 
    
    `mysqldump -u <user name> --password=<pwd> <original db> | mysql -u <user name> -p <new db>`

* show tables: 
    
    `show tables;`

* show the list of columns names in table: 

    `SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = N'<table name>';`

* selecting multiple columns: 
    
    `SELECT year, probable_cause FROM accidents;`

* selecting with condition: 
    
    `SELECT year, total_occupants, total_fatalities FROM accidents WHERE year = 2020;`

* order by ascending: 

    `SELECT year, total_occupants, total_fatalities FROM accidents WHERE year=2020 ORDER BY day;`

* order by descending: 
    
    `SELECT year, total_occupants, total_fatalities FROM accidents WHERE year = 2020 ORDER BY total_fatalities DESC;`

* select distinct values:
    
    `SELECT DISTINCT year FROM accidents;`

* count number of rows in query: 
    
    `SELECT COUNT(id) FROM accidents;`

* sum (In the same way, MIN, MAX and AVG can be used.  As we have seen above, all aggregation functions return only 1 row: 
    
    `SELECT SUM(total_fatalities) FROM accidents;`

* GROUP BY: Group by is used to group the tuples of a relation based on an attribute or group of
 attribute. It is always combined with aggregation function which is computed on group: 
 
    `SELECT year, SUM(total_occupants), SUM(total_fatalities) FROM accidents GROUP BY year;`
 
    `SELECT year, country, SUM(total_occupants), SUM(total_fatalities) FROM accidents GROUP BY year, country ORDER BY year;`

#### DDL, DML, TCL and DCL: https://www.geeksforgeeks.org/sql-ddl-dml-tcl-dcl/

* CREATE : to create objects in database
    
    `CREATE table test1 (a char(20), b int, c float);`

* ALTER : alters the structure of database
* DROP : delete objects from database
* RENAME : rename an objects


* SELECT: retrieve data from the database
* INSERT: insert data into a table
    
    `INSERT INTO test1 VALUES ('cc', 45, 45.2), ('dd', 545, 476);`


* UPDATE: update existing data within a table
* DELETE: deletes all records from a table, space for the records remain

* COMMIT: Commit command is used to permanently save any transaction
            into the database.
* ROLLBACK: This command restores the database to last committed state.
            It is also used with savepoint command to jump to a savepoint
            in a transaction.
* SAVEPOINT: Savepoint command is used to temporarily save a transaction so
            that you can rollback to that point whenever necessary.
            
* GRANT: allow specified users to perform specified tasks.
* REVOKE: cancel previously granted or denied permissions.

#### Views: https://www.geeksforgeeks.org/sql-views/

Views in SQL are kind of virtual tables. A view also has rows and columns as they are in a real 
table in the database. We can create a view by selecting fields from one or more tables present
in the database. A View can either have all the rows of a table or specific rows based on certain condition.


```sql
CREATE VIEW view_name AS
SELECT column1, column2.....
FROM table_name
WHERE condition;
```

```sql
CREATE VIEW yearly_agg AS SELECT year, COUNT(id) from accidents GROUP BY year;
```

```sql
select * from yearly_agg;
```

```sql
create view test_selection as select test1.a, test1.b, test2.e, test2.d from test1, test2 where test1.a = test2.e;
```

```sql
DROP VIEW view_name;
```

#### Comments in SQL: https://www.geeksforgeeks.org/sql-comments/

#### Constraints: https://www.geeksforgeeks.org/sql-constraints/

Constraints are the rules that we can apply on the type of data in a table. That is, we can specify the limit on the type of data that can be stored in a particular column in a table using constraints.

The available constraints in SQL are:

* NOT NULL: This constraint tells that we cannot store a null value in a column. That is, if a
 column is specified as NOT NULL then we will not be able to store null in this particular column any more.
* UNIQUE: This constraint when specified with a column, tells that all the values in the column
 must be unique. That is, the values in any row of a column must not be repeated.
* PRIMARY KEY: A primary key is a field which can uniquely identify each row in a table. And this
 constraint is used to specify a field in a table as primary key.
* FOREIGN KEY: A Foreign key is a field which can uniquely identify each row in a another table.
 And this constraint is used to specify a field as Foreign key.
* CHECK: This constraint helps to validate the values of a column to meet a particular condition. That is, it helps to ensure that the value stored in a column meets a specific condition.
* DEFAULT: This constraint specifies a default value for the column when no value is specified by
 the user.


```sql
CREATE TABLE sample_table
(
column1 data_type(size) constraint_name,
column2 data_type(size) constraint_name,
column3 data_type(size) constraint_name,
....
);
```

```sql
CREATE TABLE Student
(
ID int(6) NOT NULL,
NAME varchar(10) NOT NULL UNIQUE,
ADDRESS varchar(20),
PRIMARY KEY(ID),
C_ID int CHECK (C_ID > 0),
FOREIGN KEY (C_ID) REFERENCES Customers(C_ID),
AGE int DEFAULT 18
);
```

#### WITH clause: https://www.geeksforgeeks.org/sql-with-clause/

* The clause is used for defining a temporary relation such that the output of this temporary
 relation is available and is used by the query that is associated with the WITH clause.
* Queries that have an associated WITH clause can also be written using nested sub-queries but
 doing so add more complexity to read/debug the SQL query.
* WITH clause is not supported by all database system.
* The name assigned to the sub-query is treated as though it was an inline view or table
* The SQL WITH clause was introduced by Oracle in the Oracle 9i release 2 database.


```sql
with 
    temp_table (average_salary) as (select avg(salary) from employee) 
select name, salary from employee, temp_table 
where employee.salary > temp_table.average_salary;
```

This is equivalent to:

```sql
select name, salary from employee 
where salary > (select avg(salary) from employee);
```

Another example:

```sql
with 
    temp_1 (airline, total_salary) as (select airline, sum(salary) from employee group by airline),
    temp_2 (average_salary) as (select avg(salary) from employee) 
select airline from temp_1, temp_2 
where temp_1.total_salary > temp_2.average_salary;
```

Important Points:

* The SQL WITH clause is good when used with complex SQL statements rather than simple ones
* It also allows you to break down complex SQL queries into smaller ones which make it easy for
 debugging and processing the complex queries.
* The SQL WITH clause is basically a drop-in replacement to the normal sub-query.

#### Arithmetic Operators: https://www.geeksforgeeks.org/sql-arithmetic-operators/

* `+           [Addition]`
* `-           [Subtraction]`
* `/           [Division]`
* `*           [Multiplication]`
* `%           [Modulus]`