import datetime
from sqlalchemy import Column, Integer, String, Numeric, DateTime,ForeignKey, create_engine,func
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine("sqlite:///:memory:", echo=False)
Base = declarative_base()

#aprašoma shop klase
class Shop(Base):
    __tablename__ = "shops"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(40),nullable=False)
    address = Column(String(100))
    items = relationship("Item")

#aprašoma Item klase
class Item(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True)
    barcode = Column (String(32), unique=True)
    name = Column(String(40),nullable=False)
    description = Column(String(200),default='EMPTY')
    unit_price = Column (Numeric(10, 2),nullable=False,default=1.00)
    created_at = Column(DateTime,default=datetime.datetime.now())
    shop_id = Column(Integer, ForeignKey("shops.id"))
    shop = relationship ("Shop")
    components  = relationship ("Component")

#aprašoma Component klase
class Component(Base):
    __tablename__ = "components"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(20))
    quantity = Column(Numeric (10, 2),default=1.00)
    item_id = Column(Integer, ForeignKey("items.id"))
    item = relationship ("Item")
  

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()



#sukuriamos parduotuves modeliai
iki = Shop (name='IKI', address='Kaunas, Iki gatvė 1')
maksima = Shop (name='MAXIMA', address='Kaunas, Maksima gatvė 2')

# irašomos porduotuves i duomenu baze
session.add_all([iki,maksima])
session.commit()

#sukuriamos prekes parduotuvems
iki.items = [
    Item(barcode='112233112233', name='Žemaičių duona', unit_price=1.55),
    Item(barcode='33333222111', description='Pienas iš Žemaitijos', name='Žemaičių pienas', unit_price=2.69)
    ]

maksima.items = [
    Item(barcode='99898989898', name='Aukštaičių duona', unit_price=1.65),
    Item(barcode='99919191991', description='Pienas iš Aukštaitijos', name='Aukštaičių pienas', unit_price=2.99)
    ]

#sukurimi komponentai prekems
iki.items[0].components = [
    Component(name='Miltai', quantity=1.50),
    Component(name='Vanduo', quantity=1.00)
    ]

iki.items[1].components = [
    Component(name='Pienas', quantity=1.00)
    ]
maksima.items[0].components = [
    Component(name='Miltai', quantity=1.60),
    Component(name='Vanduo', quantity=1.10)
    ]
maksima.items[1].components = [
    Component(name='Pienas', quantity=1.10)
    ]
#irasomi pirkiniai ir ju komponentai i duomenu baze
session.add_all([iki.items[0], iki.items[1],maksima.items[0],maksima.items[1]])
session.commit()

#pakeiciamas prekes kiekis
iki.items[0].quantity = 1.45
session.add(iki.items[0])
#istrinamas prekes komponentas (kad neliktu kabanciu elementu)
session.delete(maksima.items[1].components[0])
#istrinama preke
session.delete(maksima.items[1])
#irasomi pakeitimai i duomenu baze
session.commit()


#atspausdinamos visos parduotuves, jose esancios prekes ir ju komponentai
for shop in session.query(Shop).all():
   print(shop.name)
   for item in shop.items:
       print ("   "+item.name)
       for comp in item.components:
           print ("      "+comp.name)

#atrenkamos prekes kurios turi susietu elementu
print ()
print ("prekes kurios turi susietu elementu:")

mylist = []
mylist2 = []
for shop in session.query(Shop).all():
   for item in shop.items:
       for comp in item.components:
           mylist.append(comp.name)
           
seen = set()
seen_add = seen.add
seen_twice = set( x for x in mylist if x in seen or seen_add(x) )

for shop in session.query(Shop).all():
   for item in shop.items:
       for comp in item.components:
           for seen in seen_twice:
               if seen == comp.name:
                   mylist2.append(item.name)
                   
mylist = list(dict.fromkeys(mylist2))                   

for item in mylist:
    print (item)
    
print ()
print ("prekes kuriu pavadinime yra ien :")
#atrenkamos prekes kuriu pavadinime yra "ien"   
for item in session.query(Item).filter(Item.name.like("%ien%")).all():
   print(item.name)
   

print ()
print ("kiek komponentu sudaryta preke:")
#skaiciuoja is kiek komponentu sudaryta preke   
for item, counter in session.query(Item, func.count(Component.id)).join(Component).group_by(Item).all():
   print (item.name,  counter)

print ()
#skaiciuoja is kiekvienos prekes komponentu kieki (quantity) 
for item, counter in session.query(Item, func.sum(Component.quantity)).join(Component).group_by(Item).all():
   print (item.name,  counter) 
print ()  
print ("Isfiltruojamos prekes kurios buvo sukurtos 2021 metais:")
#Isfiltruojamos prekes kurios buvo sukurtos 2021 metais
for item in session.query(Item).filter(item.created_at.year==2021):
   print(item.name)

