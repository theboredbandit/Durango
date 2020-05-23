from durango.models import Connection, User
from durango.models import db

def is_connection_or_pending(user_a_id, user_b_id):
  
    is_connection = db.session.query(Connection).filter(Connection.user_a_id == user_a_id,
                                                     Connection.user_b_id == user_b_id,
                                                     Connection.status == "Accepted").first()

    is_pending = db.session.query(Connection).filter(Connection.user_a_id == user_a_id,
                                                     Connection.user_b_id == user_b_id,
                                                     Connection.status == "Requested").first()

    return is_connection, is_pending


def get_connection_requests(user_id):

    #Get user's connection requests.
    #Returns users that user received connection requests from.
    #Returns users that user sent connection requests to.


    received_connection_requests = db.session.query(User).filter(Connection.user_b_id == user_id,
                                                             Connection.status == "Requested").join(Connection,
                                                                                                    Connection.user_a_id == User.id).all()

    sent_connection_requests = db.session.query(User).filter(Connection.user_a_id == user_id,
                                                         Connection.status == "Requested").join(Connection,
                                                                                                Connection.user_b_id == User.id).all()

    return received_connection_requests, sent_connection_requests


def get_connections(user_id):
    #This does not return User objects, just the query


    connections_1 = db.session.query(User).filter(Connection.user_a_id == user_id,
                                            Connection.status == "Accepted").join(Connection,
                                                                                  Connection.user_b_id == User.id)

    connections_2=(db.session.query(User).filter(Connection.user_b_id == user_id,
                                            Connection.status == "Accepted").join(Connection,Connection.user_a_id == User.id))
    return connections_1,connections_2
