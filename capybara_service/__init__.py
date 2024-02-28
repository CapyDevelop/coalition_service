import os
from concurrent import futures

import coalition_service.coalition_service_pb2 as coalition_service_pb2
import coalition_service.coalition_service_pb2_grpc as coalition_service_pb2_grpc
import grpc
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .generator import generate_random_hash
from .models import Peer

load_dotenv()
print(os.getenv("DB_ENGINE"))
engine = create_engine(os.getenv("DB_ENGINE"))
Session = sessionmaker(bind=engine)


class CoalitionService(coalition_service_pb2_grpc.CoalitionServiceServicer):
    def set_coalition_member(self, request, context):
        if not request.login or not request.school_user_id or not request.tribe:
            return coalition_service_pb2.SetCoalitionMemberResponse(status=1, description="Not such data")
        session = Session()
        user = session.query(Peer).filter(Peer.school_user_id == request.school_user_id).first()
        if user:
            user.is_student = True
            session.commit()
        else:
            session.add(Peer(
                login=request.login,
                school_user_id=request.school_user_id,
                tribe=request.tribe,
                is_student=True,
                key=generate_random_hash()))
            session.commit()
        session.close()
        return coalition_service_pb2.SetCoalitionMemberResponse(status=0, description="Success", is_new_member=not bool(user))

    def reset_all_members(self, request, context):
        session = Session()
        session.query(Peer).update({"is_student": False})
        session.commit()
        session.close()
        return coalition_service_pb2.Empty()

    def get_member_by_tg_id(self, request, context):
        session = Session()
        user = session.query(Peer).filter(Peer.telegram_id == request.tg_id).first()
        session.close()
        if user:
            return coalition_service_pb2.GetMemberByTgIdResponse(status=0,
                                                                 description="Success",
                                                                 school_user_id=user.school_user_id,
                                                                 login=user.login)
        else:
            return coalition_service_pb2.GetMemberByTgIdResponse(status=1, description="Not found")

    def set_tg_id_by_key(self, request, context):
        session = Session()
        print(request.key, request.tg_id)
        user = session.query(Peer).filter(Peer.key == request.key).first()
        if user:
            user.telegram_id = request.tg_id
            session.commit()
            session.close()
            return coalition_service_pb2.SetTgIdByKeyResponse(status=0, description="Success")
        else:
            session.close()
            return coalition_service_pb2.SetTgIdByKeyResponse(status=1, description="Not found")


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    coalition_service_pb2_grpc.add_CoalitionServiceServicer_to_server(CoalitionService(), server)
    server.add_insecure_port(f'[::]:{os.getenv("COALITION_GRPC_PORT")}')
    print("start on", os.getenv("COALITION_GRPC_PORT"))
    server.start()
    server.wait_for_termination()
