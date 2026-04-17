"""Authorization primitives for Matadore engagements.

Every engagement requires a :class:`ScopeToken` - a signed JWT proving that
the red team has explicit authorization to scan the target.  The asset owner
creates and signs the token; the red team passes it to
:class:`~matadore.Matadore`.

Example::

    from matadore.auth import ScopeToken

    # Asset owner creates and signs the token
    token = ScopeToken.issue(
        target="mydomain.com",
        issued_to="red-team@company.com",
        valid_until="2026-04-30",
        engagement_type="full",
    )
    signed = token.sign(private_key)

    # Red team consumes it
    from matadore import Matadore
    m = Matadore(model="gpt-4o", scope_token=signed)
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ScopeToken:
    """Signed JWT that proves authorization to scan a specific target.

    Args:
        target: Domain, IP range, GitHub org, or cloud account being authorized.
        issued_to: Identity of the authorized red team (e-mail or team name).
        valid_until: ISO-8601 date string after which the token expires.
        engagement_type: ``"full"``, ``"passive"``, or ``"stealth"``.
    """

    target: str
    issued_to: str
    valid_until: str
    engagement_type: str

    @classmethod
    def issue(
        cls,
        target: str,
        issued_to: str,
        valid_until: str,
        engagement_type: str,
    ) -> ScopeToken:
        """Create an unsigned :class:`ScopeToken`.

        Call :meth:`sign` on the returned object to produce the JWT string
        that :class:`~matadore.Matadore` accepts.
        """
        return cls(
            target=target,
            issued_to=issued_to,
            valid_until=valid_until,
            engagement_type=engagement_type,
        )

    def sign(self, private_key: str) -> str:  # noqa: ARG002
        """Sign the token with *private_key* and return a JWT string.

        Args:
            private_key: PEM-encoded RSA/EC private key owned by the asset owner.

        Returns:
            A signed JWT string suitable for passing as ``scope_token``.
        """
        raise NotImplementedError
