#!/usr/bin/env python3
"""Test the vlanport module."""

import os
import sys
import unittest
import random

# Try to create a working PYTHONPATH
EXEC_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.abspath(
    os.path.join(
        os.path.abspath(
            os.path.join(
                os.path.abspath(
                    os.path.join(
                        os.path.abspath(
                            os.path.join(
                                os.path.abspath(
                                    os.path.join(EXEC_DIR, os.pardir)
                                ),
                                os.pardir,
                            )
                        ),
                        os.pardir,
                    )
                ),
                os.pardir,
            )
        ),
        os.pardir,
    )
)
_EXPECTED = """\
{0}switchmap-ng{0}tests{0}switchmap_{0}server{0}db{0}table""".format(
    os.sep
)
if EXEC_DIR.endswith(_EXPECTED) is True:
    # We need to prepend the path in case the repo has been installed
    # elsewhere on the system using PIP. This could corrupt expected results
    sys.path.insert(0, ROOT_DIR)
else:
    print(
        """This script is not installed in the "{0}" directory. Please fix.\
""".format(
            _EXPECTED
        )
    )
    sys.exit(2)


# Create the necessary configuration to load the module
from tests.testlib_ import setup

CONFIG = setup.config()
CONFIG.save()

from switchmap.server.db.table import vlanport as testimport
from switchmap.server.db.table import zone
from switchmap.server.db.table import oui
from switchmap.server.db.table import vlan
from switchmap.server.db.table import mac
from switchmap.server.db.table import device
from switchmap.server.db.table import event
from switchmap.server.db.table import l1interface
from switchmap.server.db.models import VlanPort
from switchmap.server.db.table import IVlanPort
from switchmap.server.db.table import IVlan
from switchmap.server.db.table import IMac
from switchmap.server.db.table import IZone
from switchmap.server.db.table import IOui
from switchmap.server.db.table import IDevice
from switchmap.server.db.table import IEvent
from switchmap.server.db.table import IL1Interface
from switchmap.server.db import models

from tests.testlib_ import db
from tests.testlib_ import data


class TestDbTableVlanPort(unittest.TestCase):
    """Checks all functions and methods."""

    #########################################################################
    # General object setup
    #########################################################################

    @classmethod
    def setUp(cls):
        """Execute these steps before starting each test."""
        # Load the configuration in case it's been deleted after loading the
        # configuration above. Sometimes this happens when running
        # `python3 -m unittest discover` where another the tearDownClass of
        # another test module prematurely deletes the configuration required
        # for this module
        config = setup.config()
        config.save()

        # Create database tables
        models.create_all_tables()

        # Pollinate db with prerequisites
        db.populate()

    @classmethod
    def tearDown(cls):
        """Execute these steps after each tests is completed."""
        # Drop tables
        database = db.Database()
        database.drop()

        # Cleanup the
        CONFIG.cleanup()

    def test_idx_exists(self):
        """Testing function idx_exists."""
        # Create record
        row = _row()

        # Test before insertion of an initial row
        nonexistent = testimport.exists(row.idx_l1interface, row.idx_vlan)
        self.assertFalse(nonexistent)

        # Test after insertion of an initial row
        testimport.insert_row(row)
        preliminary_result = testimport.exists(
            row.idx_l1interface, row.idx_vlan
        )
        self.assertTrue(preliminary_result)
        self.assertEqual(_convert(preliminary_result), _convert(row))

        # Test idx_index function
        result = testimport.idx_exists(preliminary_result.idx_vlanport)
        self.assertTrue(result)
        self.assertEqual(_convert(result), _convert(preliminary_result))

    def test_exists(self):
        """Testing function exists."""
        # Create record
        row = _row()

        # Test before insertion of an initial row
        result = testimport.exists(row.idx_l1interface, row.idx_vlan)
        self.assertFalse(result)

        # Test after insertion of an initial row
        testimport.insert_row(row)
        result = testimport.exists(row.idx_l1interface, row.idx_vlan)
        self.assertTrue(result)
        self.assertEqual(_convert(result), _convert(row))

    # def test_find_idx_vlan(self):
    #     """Testing function find_idx_vlan."""
    #     # Initialize key variables
    #     finds = []

    #     # Test with known and unknown MACs
    #     for _ in range(1, db.TEST_MAXIMUM):
    #         row = _row()
    #         exists = testimport.exists(row.idx_l1interface, row.idx_vlan)
    #         if bool(exists) is False:
    #             # Entry must not be found
    #             result = testimport.find_idx_vlan(row.idx_vlan)
    #             if row.idx_vlan not in finds:
    #                 self.assertFalse(
    #                     bool(
    #                         testimport.exists(
    #                             row.idx_l1interface, row.idx_vlan
    #                         )
    #                     )
    #                 )
    #                 self.assertFalse(bool(result))
    #             else:
    #                 self.assertTrue(bool(result))
    #                 continue

    #             # Insert entry and then it should be found
    #             testimport.insert_row(row)
    #             now_exists = testimport.exists(
    #                 row.idx_l1interface, row.idx_vlan
    #             )
    #             self.assertTrue(bool(now_exists))

    #             post_result = testimport.find_idx_vlan(now_exists.idx_vlan)
    #             self.assertEqual(now_exists.idx_vlan, row.idx_vlan)
    #             self.assertTrue(bool(post_result))
    #             finds.append(now_exists.idx_vlan)
    #         else:
    #             result = testimport.find_idx_vlan(row.idx_vlan)
    #             self.assertTrue(bool(result))
    #             if exists.idx_vlan not in finds:
    #                 finds.append(exists.idx_vlan)

    def test_find_idx_vlan(self):
        """Testing function find_idx_vlan."""
        # Initialize key variables
        finds = []

        # Test with known and unknown MACs
        for _ in range(1, db.TEST_MAXIMUM):
            row = _row()
            exists = testimport.exists(row.idx_l1interface, row.idx_vlan)
            if bool(exists) is False:
                # Entry must not be found
                result = testimport.find_idx_vlan(row.idx_vlan)
                if row.idx_vlan not in finds:
                    self.assertFalse(
                        bool(
                            testimport.exists(
                                row.idx_l1interface, row.idx_vlan
                            )
                        )
                    )
                    # The combination idx_l1interface, idx_vlan must not exist
                    for item in result:
                        self.assertFalse(
                            (item.idx_l1interface != row.idx_l1interface)
                            and (item.idx_vlan != row.idx_vlan)
                        )
                else:
                    for item in result:
                        self.assertEqual(item.idx_vlan, row.idx_vlan)
                    continue

                # Insert entry and then it should be found
                testimport.insert_row(row)
                now_exists = testimport.exists(
                    row.idx_l1interface, row.idx_vlan
                )
                self.assertTrue(bool(now_exists))
                post_result = testimport.find_idx_vlan(now_exists.idx_vlan)
                self.assertEqual(now_exists.idx_vlan, row.idx_vlan)

                # Test find
                for item in post_result:
                    self.assertEqual(item.idx_vlan, row.idx_vlan)
                self.assertTrue(bool(post_result))

                # Update found idx_vlan values
                finds.append(now_exists.idx_vlan)
            else:
                result = testimport.find_idx_vlan(row.idx_vlan)

                # Test find
                for item in result:
                    self.assertEqual(item.idx_vlan, row.idx_vlan)
                    self.assertEqual(item.idx_vlan, exists.idx_vlan)

                # Update found idx_vlan values
                if exists.idx_vlan not in finds:
                    finds.append(exists.idx_vlan)

    # def test_insert_row(self):
    #     """Testing function insert_row."""
    #     # Create record
    #     row = _row()

    #     # Test before insertion of an initial row
    #     result = testimport.exists(row.idx_l1interface, row.idx_vlan)
    #     self.assertFalse(result)

    #     # Test after insertion of an initial row
    #     testimport.insert_row(row)
    #     result = testimport.exists(row.idx_l1interface, row.idx_vlan)
    #     self.assertTrue(result)
    #     self.assertEqual(_convert(result), _convert(row))

    def test_insert_row(self):
        """Testing function insert_row."""
        # Find a row combination that does not exist
        while True:
            # Create record
            row = _row()

            # Test before insertion of an initial row
            result = testimport.exists(row.idx_l1interface, row.idx_vlan)
            if bool(result) is False:
                self.assertFalse(result)
                break

        # Test after insertion of an initial row
        testimport.insert_row(row)
        result = testimport.exists(row.idx_l1interface, row.idx_vlan)
        self.assertTrue(result)
        self.assertEqual(_convert(result), _convert(row))

    def test_update_row(self):
        """Testing function update_row."""
        # Find a row combination that does not exist
        while True:
            # Create record
            row = _row()

            # Test before insertion of an initial row
            result = testimport.exists(row.idx_l1interface, row.idx_vlan)
            if bool(result) is True:
                self.assertTrue(result)
                break

        # Do an update
        idx = result.idx_vlanport
        updated_row = VlanPort(
            idx_l1interface=random.randint(1, db.TEST_MAXIMUM),
            idx_vlan=random.randint(1, db.TEST_MAXIMUM),
            enabled=row.enabled,
        )
        testimport.update_row(idx, updated_row)

        # Test the update
        result = testimport.exists(
            updated_row.idx_l1interface, updated_row.idx_vlan
        )
        self.assertTrue(result)
        self.assertEqual(_convert(result), _convert(updated_row))

    def test__row(self):
        """Testing function _row."""
        # This function is tested by all the other tests
        pass


def _convert(row):
    """Convert RVlanPort to IVlanPort record.

    Args:
        row: RVlanPort/IVlanPort record

    Returns:
        result: IVlanPort result

    """
    # Do conversion
    result = IVlanPort(
        idx_l1interface=row.idx_l1interface,
        idx_vlan=row.idx_vlan,
        enabled=row.enabled,
    )
    return result


def _row():
    """Create an IVlanPort record.

    Args:
        None

    Returns:
        result: IVlanPort object

    """
    # Create result
    result = IVlanPort(
        idx_l1interface=random.randint(1, db.TEST_MAXIMUM),
        idx_vlan=random.randint(1, db.TEST_MAXIMUM),
        enabled=1,
    )
    return result


def _prerequisites():
    """Create prerequisite rows.

    Args:
        None

    Returns:
        None

    """
    # Create result
    event_name = data.random_string()
    event.insert_row(IEvent(name=event_name, enabled=1))
    row = event.exists(event_name)
    zone.insert_row(
        IZone(
            idx_event=row.idx_event,
            name=data.random_string(),
            company_name=data.random_string(),
            address_0=data.random_string(),
            address_1=data.random_string(),
            address_2=data.random_string(),
            city=data.random_string(),
            state=data.random_string(),
            country=data.random_string(),
            postal_code=data.random_string(),
            phone=data.random_string(),
            notes=data.random_string(),
            enabled=1,
        )
    )
    oui.insert_row(
        IOui(
            oui=data.random_string(),
            organization=data.random_string(),
            enabled=1,
        )
    )
    mac.insert_row(
        [
            IMac(idx_oui=1, idx_zone=1, mac=data.mac(), enabled=1)
            for _ in range(db.TEST_MAXIMUM)
        ]
    )
    device.insert_row(
        IDevice(
            idx_zone=1,
            sys_name=data.random_string(),
            hostname=data.random_string(),
            name=data.random_string(),
            sys_description=data.random_string(),
            sys_objectid=data.random_string(),
            sys_uptime=random.randint(0, 1000000),
            last_polled=random.randint(0, 1000000),
            enabled=1,
        )
    )
    l1interface.insert_row(
        [
            IL1Interface(
                idx_device=1,
                ifindex=random.randint(0, 1000000),
                duplex=random.randint(0, 1000000),
                ethernet=1,
                nativevlan=random.randint(0, 1000000),
                trunk=1,
                ifspeed=random.randint(0, 1000000),
                ifalias=data.random_string(),
                ifdescr=data.random_string(),
                ifadminstatus=random.randint(0, 1000000),
                ifoperstatus=random.randint(0, 1000000),
                ts_idle=random.randint(0, 1000000),
                cdpcachedeviceid=data.random_string(),
                cdpcachedeviceport=data.random_string(),
                cdpcacheplatform=data.random_string(),
                lldpremportdesc=data.random_string(),
                lldpremsyscapenabled=data.random_string(),
                lldpremsysdesc=data.random_string(),
                lldpremsysname=data.random_string(),
                enabled=1,
            )
            for _ in range(db.TEST_MAXIMUM)
        ]
    )
    vlan.insert_row(
        [
            IVlan(
                idx_device=1,
                vlan=random.randint(0, 1000000),
                name=data.random_string(),
                state=random.randint(0, 1000000),
                enabled=1,
            )
            for _ in range(db.TEST_MAXIMUM)
        ]
    )


if __name__ == "__main__":
    # Do the unit test
    unittest.main()
