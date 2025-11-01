"""
Unit tests for ProductRepository with comprehensive edge case coverage.

Tests cover:
- Happy path scenarios
- Edge cases (empty results, null values, boundary conditions)
- Error conditions (invalid IDs, missing data)
- Data validation

Marking Criteria: 4.1 (Testing and Quality Assurance)
"""
import pytest
from app.repositories.product_repository import ProductRepository
from app.domain.product import Product


class TestProductRepository:
    """Test suite for ProductRepository with edge cases."""

    # ==================== FIND BY ID Tests ====================

    def test_find_by_id_success(self, db_session, test_product):
        """Test finding product by valid ID - happy path."""
        repo = ProductRepository(db_session)
        product = repo.find_by_id(test_product.id)

        assert product is not None
        assert product.id == test_product.id
        assert product.sku == "TEST-001"
        assert product.name == "Test Product"

    def test_find_by_id_nonexistent(self, db_session):
        """Test finding product with non-existent ID returns None."""
        repo = ProductRepository(db_session)
        product = repo.find_by_id(99999)

        assert product is None

    def test_find_by_id_negative(self, db_session):
        """Test finding product with negative ID returns None."""
        repo = ProductRepository(db_session)
        product = repo.find_by_id(-1)

        assert product is None

    def test_find_by_id_zero(self, db_session):
        """Test finding product with ID zero returns None."""
        repo = ProductRepository(db_session)
        product = repo.find_by_id(0)

        assert product is None

    # ==================== FIND BY SKU Tests ====================

    def test_find_by_sku_success(self, db_session, test_product):
        """Test finding product by valid SKU - happy path."""
        repo = ProductRepository(db_session)
        product = repo.find_by_sku("TEST-001")

        assert product is not None
        assert product.sku == "TEST-001"
        assert product.id == test_product.id

    def test_find_by_sku_nonexistent(self, db_session):
        """Test finding product with non-existent SKU returns None."""
        repo = ProductRepository(db_session)
        product = repo.find_by_sku("NONEXISTENT-SKU")

        assert product is None

    def test_find_by_sku_empty_string(self, db_session):
        """Test finding product with empty SKU returns None."""
        repo = ProductRepository(db_session)
        product = repo.find_by_sku("")

        assert product is None

    def test_find_by_sku_case_sensitive(self, db_session, test_product):
        """Test SKU search is case-sensitive."""
        repo = ProductRepository(db_session)
        product = repo.find_by_sku("test-001")  # lowercase

        # Should not find because SKU is "TEST-001"
        assert product is None

    # ==================== FIND ALL Tests ====================

    def test_find_all_with_products(self, db_session, test_products):
        """Test finding all products when database has products."""
        repo = ProductRepository(db_session)
        products = repo.find_all()

        assert len(products) == 5
        assert all(p.is_active for p in products)

    def test_find_all_empty_database(self, db_session):
        """Test finding all products when database is empty."""
        repo = ProductRepository(db_session)
        products = repo.find_all()

        assert products == []

    def test_find_all_with_limit(self, db_session, test_products):
        """Test finding all products with limit parameter."""
        repo = ProductRepository(db_session)
        products = repo.find_all(limit=2)

        assert len(products) == 2

    def test_find_all_with_skip(self, db_session, test_products):
        """Test finding all products with skip parameter."""
        repo = ProductRepository(db_session)
        products = repo.find_all(skip=2)

        assert len(products) == 3

    def test_find_all_skip_exceeds_total(self, db_session, test_products):
        """Test skip parameter exceeding total products returns empty list."""
        repo = ProductRepository(db_session)
        products = repo.find_all(skip=100)

        assert products == []

    def test_find_all_excludes_inactive(self, db_session, test_product):
        """Test that inactive products are excluded from results."""
        repo = ProductRepository(db_session)

        # Deactivate the product
        test_product.is_active = False
        db_session.commit()

        products = repo.find_all()
        assert len(products) == 0

    # ==================== SEARCH Tests ====================

    def test_search_by_name_match(self, db_session, test_products):
        """Test searching products by name - happy path."""
        repo = ProductRepository(db_session)
        products = repo.search("Product 1")

        assert len(products) == 1
        assert "Product 1" in products[0].name

    def test_search_partial_match(self, db_session, test_products):
        """Test searching with partial name match."""
        repo = ProductRepository(db_session)
        products = repo.search("Product")

        # Should match all test products
        assert len(products) >= 5

    def test_search_case_insensitive(self, db_session, test_products):
        """Test search is case-insensitive."""
        repo = ProductRepository(db_session)
        products = repo.search("PRODUCT")

        assert len(products) >= 5

    def test_search_no_results(self, db_session, test_products):
        """Test search with no matching products."""
        repo = ProductRepository(db_session)
        products = repo.search("NonExistentProduct")

        assert products == []

    def test_search_empty_query(self, db_session, test_products):
        """Test search with empty query string."""
        repo = ProductRepository(db_session)
        products = repo.search("")

        # Empty search should match all products (wildcard %%)
        assert len(products) >= 5

    def test_search_with_limit(self, db_session, test_products):
        """Test search respects limit parameter."""
        repo = ProductRepository(db_session)
        products = repo.search("Product", limit=2)

        assert len(products) == 2

    # ==================== FIND BY CATEGORY Tests ====================

    def test_find_by_category_match(self, db_session, test_products):
        """Test finding products by category - happy path."""
        repo = ProductRepository(db_session)
        products = repo.find_by_category("test")

        # test_products creates products with alternating categories
        assert len(products) >= 2
        assert all(p.category == "test" for p in products)

    def test_find_by_category_no_match(self, db_session, test_products):
        """Test finding products by non-existent category."""
        repo = ProductRepository(db_session)
        products = repo.find_by_category("nonexistent")

        assert products == []

    def test_find_by_category_case_sensitive(self, db_session, test_products):
        """Test category search is case-sensitive."""
        repo = ProductRepository(db_session)
        products = repo.find_by_category("TEST")  # uppercase

        # Should not match "test"
        assert len(products) == 0

    # ==================== CREATE Tests ====================

    def test_create_product_success(self, db_session):
        """Test creating new product - happy path."""
        repo = ProductRepository(db_session)

        product = Product(
            sku="NEW-001",
            name="New Product",
            description="A new product",
            price=50.00,
            category="new",
            brand="TestBrand",
            color="blue",
            features="test",
            image_url="http://example.com/new.png",
            is_active=True
        )

        created = repo.create(product)

        assert created.id is not None
        assert created.sku == "NEW-001"
        assert created.price == 50.00

    def test_create_product_minimal_fields(self, db_session):
        """Test creating product with only required fields."""
        repo = ProductRepository(db_session)

        product = Product(
            sku="MINIMAL-001",
            name="Minimal Product",
            price=10.00,
            category="minimal",
            is_active=True
        )

        created = repo.create(product)

        assert created.id is not None
        assert created.description is None  # Optional field

    # ==================== UPDATE Tests ====================

    def test_update_product_success(self, db_session, test_product):
        """Test updating product - happy path."""
        repo = ProductRepository(db_session)

        test_product.price = 150.00
        test_product.name = "Updated Product"

        updated = repo.update(test_product)

        assert updated.price == 150.00
        assert updated.name == "Updated Product"

    def test_update_product_price_to_zero(self, db_session, test_product):
        """Test updating product price to zero."""
        repo = ProductRepository(db_session)

        test_product.price = 0.00
        updated = repo.update(test_product)

        assert updated.price == 0.00

    # ==================== DELETE (Soft Delete) Tests ====================

    def test_delete_product_success(self, db_session, test_product):
        """Test soft deleting product - happy path."""
        repo = ProductRepository(db_session)

        result = repo.delete(test_product.id)

        assert result is True

        # Verify product still exists but is inactive
        product = repo.find_by_id(test_product.id)
        assert product is not None
        assert product.is_active is False

    def test_delete_nonexistent_product(self, db_session):
        """Test deleting non-existent product returns False."""
        repo = ProductRepository(db_session)

        result = repo.delete(99999)

        assert result is False

    def test_delete_already_deleted(self, db_session, test_product):
        """Test deleting already deleted product."""
        repo = ProductRepository(db_session)

        # Delete once
        repo.delete(test_product.id)

        # Delete again
        result = repo.delete(test_product.id)

        assert result is True  # Should still return True
