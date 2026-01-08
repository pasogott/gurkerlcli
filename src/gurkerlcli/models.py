"""Pydantic models for API responses."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    """Product search result (from /api/v1/products + /api/v1/products/prices)."""

    id: int
    name: str
    slug: str
    brand: str | None = None
    unit: str
    textual_amount: str = Field(alias="textualAmount")
    images: list[str] = Field(default_factory=list)
    price: Decimal | None = None
    price_per_unit: Decimal | None = None
    currency: str = "EUR"

    class Config:
        populate_by_name = True

    @property
    def image_url(self) -> str:
        """Get first image URL."""
        return self.images[0] if self.images else ""

    @property
    def price_display(self) -> str:
        """Get formatted price."""
        if self.price is not None:
            return f"€ {self.price:.2f}"
        return "N/A"


class ProductImage(BaseModel):
    """Product image."""

    path: str
    backgroundColor: str | None = None


class ProductPrices(BaseModel):
    """Product pricing."""

    originalPrice: Decimal
    salePrice: Decimal | None = None
    unitPrice: Decimal
    currency: str = "EUR"


class ProductStock(BaseModel):
    """Product stock info."""

    maxAvailableAmount: int
    availabilityStatus: str
    availabilityReason: str | None = None


class Product(BaseModel):
    """Product model."""

    productId: int
    name: str
    slug: str
    image: ProductImage
    prices: ProductPrices
    stock: ProductStock
    unit: str
    textualAmount: str
    brand: str | None = None

    @property
    def id(self) -> str:
        """Get product ID as string."""
        return str(self.productId)

    @property
    def price(self) -> Decimal:
        """Get current price."""
        return self.prices.salePrice or self.prices.originalPrice

    @property
    def image_url(self) -> str:
        """Get image URL."""
        return self.image.path

    @property
    def in_stock(self) -> bool:
        """Check if product is in stock."""
        return self.stock.availabilityStatus == "AVAILABLE"


class CartItemDTO(BaseModel):
    """Cart item from API (raw format)."""

    productId: int
    orderFieldId: int
    imgPath: str
    productName: str
    link: str
    baseLink: str
    quantity: int
    volume: str
    unit: str
    maxBasketAmount: int
    maxBasketAmountReason: str
    salePercents: int = 0
    discountPrice: Decimal | None = None
    originalPrice: Decimal | None = None
    originalPricePerUnit: Decimal
    asPriceDiff: bool
    saleId: int | None = None
    saleType: str | None = None
    billablePackagingPriceVAT: Decimal
    price: Decimal
    recommendedPricePerUnit: Decimal
    currency: str = "EUR"
    companyName: str
    companyId: int
    textualAmount: str
    primaryCategoryName: str | None = None
    semicaliber: bool
    brand: str | None = None
    availabilityDimension: int
    silent: bool
    singlePieceDeposit: Decimal
    lastMinute: bool
    favourite: bool
    deposit: Decimal
    isLastMinute: bool

    @property
    def subtotal(self) -> Decimal:
        """Calculate subtotal."""
        return self.price * self.quantity

    @property
    def image_url(self) -> str:
        """Get full image URL."""
        return f"https://www.gurkerl.at{self.imgPath}"

    @property
    def has_discount(self) -> bool:
        """Check if item has discount."""
        return self.salePercents > 0


class CartCategoryDTO(BaseModel):
    """Cart category grouping."""

    id: int
    name: str
    position: int
    items: list[int]  # List of productIds
    topMessages: list[str] = Field(default_factory=list)
    bottomMessages: list[str] = Field(default_factory=list)


class CartCompanyDTO(BaseModel):
    """Company in cart."""

    id: int
    name: str
    label: str
    link: str
    categories: list[int]


class CartDataDTO(BaseModel):
    """Cart data from API."""

    cartId: int
    totalPrice: Decimal
    totalSavings: Decimal
    minimalStandardOrderPrice: Decimal
    minimalDeliveryPointOrderPrice: Decimal
    premiumSavings: Decimal | None = None
    deliveryPointEnabled: bool
    submitConditionPassed: bool
    companies: list[CartCompanyDTO]
    categories: dict[str, CartCategoryDTO]
    items: dict[str, CartItemDTO]  # Key is productId as string
    gifts: list[dict] = Field(default_factory=list)
    notAvailableItems: list[dict] = Field(default_factory=list)
    notCriticalChanges: bool
    freeDeliveryRemainingAmount: Decimal
    minimalOrderPrice: Decimal


class CartResponseDTO(BaseModel):
    """Full cart API response."""

    status: int
    messages: list[str] = Field(default_factory=list)
    data: CartDataDTO


class CartItem(BaseModel):
    """Simplified cart item for display."""

    product_id: int
    order_field_id: int
    name: str
    brand: str | None
    quantity: int
    price: Decimal
    subtotal: Decimal
    image_url: str
    unit: str
    textual_amount: str
    has_discount: bool
    sale_percents: int = 0
    original_price: Decimal | None = None

    @classmethod
    def from_dto(cls, dto: CartItemDTO) -> CartItem:
        """Create from DTO."""
        return cls(
            product_id=dto.productId,
            order_field_id=dto.orderFieldId,
            name=dto.productName,
            brand=dto.brand,
            quantity=dto.quantity,
            price=dto.price,
            subtotal=dto.subtotal,
            image_url=dto.image_url,
            unit=dto.unit,
            textual_amount=dto.textualAmount,
            has_discount=dto.has_discount,
            sale_percents=dto.salePercents,
            original_price=dto.originalPrice,
        )


class Cart(BaseModel):
    """Shopping cart model."""

    cart_id: int
    items: list[CartItem] = Field(default_factory=list)
    total: Decimal = Decimal("0")
    item_count: int = 0
    total_savings: Decimal = Decimal("0")
    minimal_order_price: Decimal = Decimal("39.00")
    submit_condition_passed: bool = False

    @classmethod
    def from_response(cls, response: CartResponseDTO) -> Cart:
        """Create from API response."""
        data = response.data
        items = [CartItem.from_dto(dto) for dto in data.items.values()]
        return cls(
            cart_id=data.cartId,
            items=items,
            total=data.totalPrice,
            item_count=len(items),
            total_savings=data.totalSavings,
            minimal_order_price=data.minimalOrderPrice,
            submit_condition_passed=data.submitConditionPassed,
        )


class Order(BaseModel):
    """Order model."""

    id: str
    order_number: str
    date: datetime
    status: str
    total: Decimal
    items: list[CartItem] = Field(default_factory=list)


class ShoppingListProduct(BaseModel):
    """Product in shopping list."""

    productId: int
    amount: int
    checked: bool = False


class ShoppingList(BaseModel):
    """Shopping list model."""

    id: int
    name: str
    type: str = "GENERAL"
    products: list[ShoppingListProduct] = Field(default_factory=list)
    userId: int | None = None
    readOnly: bool = False
    shared: bool = False
    actions: list[str] = Field(default_factory=list)
