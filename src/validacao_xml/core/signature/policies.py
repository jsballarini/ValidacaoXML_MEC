"""Constantes de políticas de assinatura ICP-Brasil."""

from __future__ import annotations

# OIDs comuns de políticas de assinatura (PAdES/XAdES ICP-Brasil)
POLICY_AD_RA = "2.16.76.1.7.1.1.1"
POLICY_AD_RC = "2.16.76.1.7.1.2.1"
POLICY_AD_RB = "2.16.76.1.7.1.3.1"
POLICY_AD_RT = "2.16.76.1.7.1.4.1"

ARCHIVE_POLICIES = {POLICY_AD_RA}

ICP_BRASIL_OIDS = {
    "2.16.76.1.4.1": "A1",
    "2.16.76.1.4.2": "A2",
    "2.16.76.1.4.3": "A3",
    "2.16.76.1.4.4": "A4",
}
