#reference for pivoting stuff
class Item(Base):

    __tablename__ = 'Item'
    UniqueId = Column(Integer, ForeignKey('ItemSet.UniqueId'),
                      primary_key=True)
    ItemSet = relation('ItemSet')
    ItemName = Column(String(10), primary_key=True)
    ItemValue = Column(Text) # Use PickleType?

def _create_item(ItemName, ItemValue):
    return Item(ItemName=ItemName, ItemValue=ItemValue)

class ItemSet(Base):

    __tablename__ = 'ItemSet'
    UniqueId = Column(Integer, primary_key=True)
    _items = relation(Item,
                      collection_class=attribute_mapped_collection('ItemName'))
    items = association_proxy('_items', 'ItemValue', creator=_create_item)

engine = create_engine('sqlite://', echo=True)
metadata.create_all(engine)

session = sessionmaker(bind=engine)()
data = {"user_id": 2, 1: 0.2, 2: 0.4, 3: 0.4}
s = ModuleUserSettingsSet(user_id=data.pop('user_id'))
s.weights = data
session.add(s)
session.commit()
