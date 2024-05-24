from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, BigInteger, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class Product(Base):
    __tablename__ = 'product'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    image: Mapped[str] = mapped_column(String(150))
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text)
    section: Mapped[str] = mapped_column(String(150), nullable=False)
    category: Mapped[str] = mapped_column(String(150), nullable=False)
    gender: Mapped[str] = mapped_column(String(150), nullable=False)
    size: Mapped[str] = mapped_column(String(150), nullable=False)
    price: Mapped[str] = mapped_column(String(150), nullable=False)


# ------------------> info <--------------------
'''
      1. `id`: Уникальный идентификатор продукта.
      2. `image`: URL или путь к изображению продукта.
      3. `name`: Название продукта (обязательное поле).
      4. `description`: Описание продукта.
      5. `section`: Секция или категория, к которой относится продукт.
      6. `category`: Конкретная категория продукта внутри секции.
      7. `gender`: Пол, для которого предназначен продукт.
      8. `size`: Размер продукта.
      9. `price`: Цена продукта.
'''
