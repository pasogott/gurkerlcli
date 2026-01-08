"""Pytest configuration and fixtures."""

import pytest
from datetime import datetime, timedelta

from gurkerlcli.config import Session
from gurkerlcli.models import Product, CartItem, Cart, Order


@pytest.fixture
def mock_session():
    """Create a mock session."""
    return Session(
        cookies={"session": "test-session-cookie"},
        user_email="test@example.com",
        created_at=datetime.now(),
        expires_at=datetime.now() + timedelta(days=7),
    )


@pytest.fixture
def mock_product():
    """Create a mock product."""
    return Product(
        id="12345",
        name="Bio Milch 1L",
        price=2.49,
        unit="1L",
        in_stock=True,
        category="Milchprodukte",
    )


@pytest.fixture
def mock_cart_item(mock_product):
    """Create a mock cart item."""
    return CartItem(
        product=mock_product,
        quantity=2,
        subtotal=4.98,
    )


@pytest.fixture
def mock_cart(mock_cart_item):
    """Create a mock cart."""
    return Cart(
        items=[mock_cart_item],
        total=4.98,
        item_count=1,
    )


@pytest.fixture
def mock_order(mock_cart_item):
    """Create a mock order."""
    return Order(
        id="1",
        order_number="G-123456",
        date=datetime.now(),
        status="Delivered",
        total=4.98,
        items=[mock_cart_item],
    )
