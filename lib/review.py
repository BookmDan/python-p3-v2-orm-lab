from __init__ import CURSOR, CONN
from department import Department
from employee import Employee


class Review:

    # Dictionary of objects saved to the database.
    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    def __repr__(self):
        return (
            f"<Review {self.id}: {self.year}, {self.summary}, "
            + f"Employee: {self.employee_id}>"
        )

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        if not isinstance(value, int):
            raise ValueError("Year must be an integer.")
        if value < 2000:
            raise ValueError("Year must be greater than or equal to 2000.")
        self._year = value

    @classmethod
    def create_table(cls):
        """ Create a new table to persist the attributes of Review instances """
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            year INT,
            summary TEXT,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employee(id))
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """ Drop the table that persists Review  instances """
        sql = """
            DROP TABLE IF EXISTS reviews;
        """
        CURSOR.execute(sql)
        CONN.commit()

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        if not value or not isinstance(value, str):
            raise ValueError("Summary must be a non-empty string.")
        self._summary = value


    def save(self):
        """ Insert a new row with the year, summary, and employee id values of the current Review object.
        Update object id attribute using the primary key value of new row.
        Save the object in local dictionary using table row's PK as dictionary key"""
        sql = """
            INSERT INTO reviews (year, summary, employee_id)
            VALUES (?, ?, ?)
        """
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id))
        CONN.commit()

        # Update the object id attribute using the primary key value of the new row
        self.id = CURSOR.lastrowid

        # Save the object in the local dictionary using the table row's PK as the dictionary key
        Review.all[self.id] = self

    @classmethod
    def create(cls, year, summary, employee_id):
        """ Initialize a new Review instance and save the object to the database. Return the new instance. """
        review = cls(year, summary, employee_id)
        review.save()
        return review
   
    @classmethod
    def instance_from_db(cls, row):
        """Return an Review instance having the attribute values from the table row."""
        # Check the dictionary for  existing instance using the row's primary key
        review_id, year, summary, employee_id = row
        return cls(id=review_id, year=year, summary=summary, employee_id=employee_id)

    @classmethod
    def find_by_id(cls, review_id):
        """Return a Review instance having the attribute values from the table row."""
        sql = """
            SELECT * FROM reviews
            WHERE id = ?
        """
        row = CURSOR.execute(sql, (review_id,)).fetchone()
        if row:
            return cls.instance_from_db(row)
        else:
            return None

    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, value):
        # Check if the employee_id exists in the employees table
        if value is not None and not Employee.find_by_id(value):
            raise ValueError("Invalid employee_id. Employee does not exist.")
        self._employee_id = value


    def update(self):
        """Update the table row corresponding to the current Review instance."""
        sql = """
            UPDATE reviews
            SET year=?, summary=?, employee_id=?
            WHERE id=?
        """
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id, self.id))
        CONN.commit()

    def delete(self):
        """Delete the table row corresponding to the current Review instance,
        delete the dictionary entry, and reassign id attribute"""
        sql = """
            DELETE FROM reviews
            WHERE id=?
        """
        CURSOR.execute(sql, (self.id,))
        CONN.commit()

        # del Review.all[self.id]
        # Set id to None after deletion
        self.id = None
        # Remove the instance from the all dictionary
        if self.id in self.all:
            del self.all[self.id]

    @classmethod
    def get_all(cls):
        """Return a list containing one Review instance per table row"""
        sql = """
            SELECT * FROM reviews
        """
        rows = CURSOR.execute(sql).fetchall()
        return [cls.instance_from_db(row) for row in rows]

    def __str__(self):
        return f"Review(id={self.id}, year={self.year}, summary={self.summary}, employee_id={self.employee_id})"