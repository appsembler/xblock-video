"""
Page elements to use with page objects.

Reference: https://selenium-python.readthedocs.io/page-objects.html#page-elements
"""

from selenium.webdriver.support.ui import WebDriverWait


class IdPageElement:
    """
    Page element wich finds itself by id attribute.
    """

    def __get__(self, obj, owner):
        """
        Get the element of the specified object.
        """
        driver = obj.driver
        WebDriverWait(driver, 100).until(
            lambda driver: driver.find_element_by_id(self.locator))  # pylint: disable=no-member
        element = driver.find_element_by_id(self.locator)  # pylint: disable=no-member
        return element


class ClassPageElement:
    """
    Page element wich finds itself by class attribute.
    """

    def __get__(self, obj, owner):
        """
        Get the element of the specified object.
        """
        driver = obj.driver
        WebDriverWait(driver, 100).until(
            lambda driver: driver.find_element_by_class_name(self.locator))  # pylint: disable=no-member
        element = driver.find_element_by_class_name(self.locator)  # pylint: disable=no-member
        return element
