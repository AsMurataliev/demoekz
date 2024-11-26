from fastapi import FastAPI, Form, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated, Optional
import datetime

def complete_count():
    return len([o for o in repo if o.status == "завершена"])

def get_problem_type_stat():
    dict = {}
    for x in repo:
        if x.etap in dict.keys():
            dict[x.etap] += 1
        else:
            dict[x.etap] = 1
    return dict

def get_average_time_to_complete():
    times = [
        datetime.datetime.fromisoformat(o.endDate.isoformat()) -
        datetime.datetime.fromisoformat(o.startDate.isoformat()).days
                 for x in repo 
                 if x.status == "завершена"]
    if complete_count() != 0:
        return sum(times) / complete_count()
    return 0

class Order(BaseModel):
  number: int
  startDate: datetime.date
  endDate: Optional[datetime.date] = None
  type_device: str
  model: str
  description: str
  fio: str
  num_tel: str
  status: Optional[str] = "Новая заявка"
  master: Optional[str] = "Не назначен"
  comments: Optional[list] = []
  etap: Optional[str] = "в процессе ремонта"


class UpdateOrderDTO(BaseModel):
  description: Optional[str] = ""
  master: Optional[str] = ""
  comment: Optional[str] = str
  etap: Optional[str]


repo= []
message = ""

app = FastAPI()

app.add_middleware(
  CORSMiddleware,
  allow_origins = ["*"],
  allow_methods = ["*"],
  allow_headers = ["*"]
)


#Получение списка заявок
@app.get("/orders")
def get_orders(param = None):
    global message
    upd = message
    message = ""
    if(param):
        return { "repo": [x for x in repo if x.number == int(param)],"message": message}
    return {"repo" : repo ,"message" : upd}

#Получение заказов по номеру.
@app.get("/number/{number}")
def get_by_number(number):
    for x in repo:
        if x.number == int(number):
            return x
    return "Order not found"


#Получение заяки по параметрам
@app.get("/filter/{param}")
def get_by_param(param):
    return [upd for upd in repo if upd.type_device == param or upd.model == param or upd.description == param or upd.num_tel == param or upd.status == param or upd.master == param]

#количество всех выполненых заявок.
@app.get("/completeCounts")
def complete_counts():
    return complete_count()



@app.post("/update")
def update_order(dto: Annotated[UpdateOrderDTO , Form()]):
    global message
    for x in repo:
        if x.number == dto.number:
            if dto.status != x.status and dto.status != "":
                x.status = dto.status
                message += f"Статус заявки №${o.number} изменен\n"
                if(x.status == "завершена"):
                    message += f"Заявки №{o.number} Завершено\n"
                    x.endDate = datetime.datetime.now()
            if dto.description != "":
                x.description = dto.description
            if dto.master != "":
                x.master = dto.master
            if dto.comment != None and dto.comment != "":
                x.comments.append(dto.comment)
            if dto.etap != "":
                x.etap = dto.etap
            return x
    return "Не найдено"



@app.get("/statistics")
def get_statistics():
    return {
        "complete_count": complete_count(),
        "problem_type_stat": get_problem_type_stat(),
        "average_time_to_complete": get_average_time_to_complete}