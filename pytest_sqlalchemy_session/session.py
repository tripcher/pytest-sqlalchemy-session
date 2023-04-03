import logging

from sqlalchemy import exc as sa_exc
from sqlalchemy.orm import Session, SessionTransaction

logger = logging.getLogger(__name__)


class TestSession(Session):
    def begin(
        self,
        subtransactions: bool = False,
        nested: bool = False,
        _subtrans: bool = False,
    ) -> SessionTransaction:
        if subtransactions or nested or _subtrans:
            fake_nested = False
        else:
            nested = True
            fake_nested = True

        if (
            fake_nested
            and self._transaction is not None
            and getattr(self._transaction, "fake_nested", False)
        ):
            raise sa_exc.InvalidRequestError(
                "A transaction is already begun on this Session."
            )

        transaction = super().begin(
            subtransactions=subtransactions, nested=nested, _subtrans=_subtrans
        )
        transaction.fake_nested = fake_nested

        return transaction
