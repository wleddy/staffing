
import sys
#print(sys.path)
sys.path.append('') ##get import to look in the working dir.

import os
import pytest
import tempfile

import app
from staffing.models import Job, JobRole
from shotglass2.users.models import Role

@pytest.fixture
def client():
    db_fd, app.app.config['DATABASE_PATH'] = tempfile.mkstemp()
    app.app.config['TESTING'] = True
    client = app.app.test_client()

    with app.app.app_context():
        print(app.app.config['DATABASE_PATH'])
        app.init_db(app.get_db(app.app.config['DATABASE_PATH']))
        # Add some more users
        f = open('users/views/test/test_data_create.sql','r')
        sql = f.read()
        f.close()
        cur = app.g.db.cursor()
        cur.executescript(sql)
        # doris and John need passwords
        rec = app.User(app.g.db).get('doris')
        rec.password = getPasswordHash('password')
        app.User(app.g.db).save(rec)
        rec = app.User(app.g.db).get('John')
        rec.password = getPasswordHash('password')
        app.User(app.g.db).save(rec)
        app.g.db.commit()
        
        rec = app.User(app.g.db).get('doris')
        print(rec)
        rec = app.User(app.g.db).get('John')
        print(rec)
        
    yield client

    os.close(db_fd)
    os.unlink(app.app.config['DATABASE_PATH'])
    
    
filespec = 'instance/test_job_roles.db'
db = None


with app.app.app_context():
    db = app.get_db(filespec)
    app.init_db(db)

        
def delete_test_db():
        os.remove(filespec)

    
def test_job_roles():
    role_table = Role(db)
    job_table = Job(db)
    job_role_table = JobRole(db)

    role_rec = role_table.new()
    role_rec.name = "Test_Role"
    role_rec.rank = 3
    role_table.save(role_rec)
    
    job_rec = job_table.new()
    job_rec.title = "test job"
    job_table.save(job_rec)
    
    job_role_rec = job_role_table.new()
    job_role_rec.job_id = job_rec.id
    job_role_rec.role_id = role_rec.id
    job_role_table.save(job_role_rec)
    
    db.commit()
    
    assert job_role_table.select(where="role_id = {} and job_id = {}".format(role_rec.id,job_rec.id)) is not None
    
    """Test that deleting a job deletes the job_role record"""
    
    job_table.delete(job_rec.id)
    
    assert job_role_table.select() is  None #should have no records
    
    # test that deleting a role record also deletes the related JobRole record
    job_rec = job_table.new()
    job_rec.title = "test job"
    job_table.save(job_rec)
    
    job_role_rec = job_role_table.new()
    job_role_rec.job_id = job_rec.id
    job_role_rec.role_id = role_rec.id
    job_role_table.save(job_role_rec)
    
    db.commit()
    
    # there should be a role_job record
    assert job_role_table.select(where="role_id = {} and job_id = {}".format(role_rec.id,job_rec.id)) is not None
    # now delete the role
    role_table.delete(role_rec.id)
    assert role_table.select(where="name = 'Test_Role'") is None
    assert job_role_table.select() is  None #should have no records
    
    
############################ The final 'test' ########################
######################################################################
def test_finished():
    try:
        db.close()
        delete_test_db()
        assert True
    except:
        assert True
