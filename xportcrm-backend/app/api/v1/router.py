from fastapi import APIRouter
from app.api.v1.endpoints import currency, auth
from app.api.v1.generic_master_router import build_master_router

from app.models.port import Port
from app.models.incoterm import Incoterm
from app.models.container_type import ContainerType
from app.models.charge_head import ChargeHead
from app.models.airport import Airport
from app.models.vessel import Vessel
from app.models.airline import Airline
from app.models.unit_of_measure import UnitOfMeasure
from app.models.hs_code import HSCode
from app.models.service_type import ServiceType
from app.models.lead_source import LeadSourceMaster
from app.models.industry_type import IndustryType
from app.models.document_type import DocumentType
from app.models.quote_tnc_template import QuoteTncTemplate

from app.schemas.port import PortCreate, PortUpdate, PortRead
from app.schemas.incoterm import IncotermCreate, IncotermUpdate, IncotermRead
from app.schemas.container_type import ContainerTypeCreate, ContainerTypeUpdate, ContainerTypeRead
from app.schemas.charge_head import ChargeHeadCreate, ChargeHeadUpdate, ChargeHeadRead
from app.schemas.airport import AirportCreate, AirportUpdate, AirportRead
from app.schemas.vessel import VesselCreate, VesselUpdate, VesselRead
from app.schemas.airline import AirlineCreate, AirlineUpdate, AirlineRead
from app.schemas.unit_of_measure import UnitOfMeasureCreate, UnitOfMeasureUpdate, UnitOfMeasureRead
from app.schemas.hs_code import HSCodeCreate, HSCodeUpdate, HSCodeRead
from app.schemas.service_type import ServiceTypeCreate, ServiceTypeUpdate, ServiceTypeRead
from app.schemas.lead_source_master import LeadSourceMasterCreate, LeadSourceMasterUpdate, LeadSourceMasterRead
from app.schemas.industry_type import IndustryTypeCreate, IndustryTypeUpdate, IndustryTypeRead
from app.schemas.document_type import DocumentTypeCreate, DocumentTypeUpdate, DocumentTypeRead
from app.schemas.quote_tnc_template import QuoteTncTemplateCreate, QuoteTncTemplateUpdate, QuoteTncTemplateRead

from app.api.v1.endpoints import account
from app.api.v1.endpoints import contact
from app.api.v1.endpoints import lead
from app.api.v1.endpoints import opportunity
from app.api.v1.endpoints import quotation
from app.api.v1.endpoints import activity
from app.api.v1.endpoints import role

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(currency.router, prefix="/currencies", tags=["Currency Master"])

api_router.include_router(build_master_router(Port, PortCreate, PortUpdate, PortRead), prefix="/ports", tags=["Port Master"])
api_router.include_router(build_master_router(Incoterm, IncotermCreate, IncotermUpdate, IncotermRead), prefix="/incoterms", tags=["Incoterms Master"])
api_router.include_router(build_master_router(ContainerType, ContainerTypeCreate, ContainerTypeUpdate, ContainerTypeRead), prefix="/container-types", tags=["Container Type Master"])
api_router.include_router(build_master_router(ChargeHead, ChargeHeadCreate, ChargeHeadUpdate, ChargeHeadRead), prefix="/charge-heads", tags=["Charge Head Master"])
api_router.include_router(build_master_router(Airport, AirportCreate, AirportUpdate, AirportRead), prefix="/airports", tags=["Airport Master"])
api_router.include_router(build_master_router(Vessel, VesselCreate, VesselUpdate, VesselRead), prefix="/vessels", tags=["Vessel Master"])
api_router.include_router(build_master_router(Airline, AirlineCreate, AirlineUpdate, AirlineRead), prefix="/airlines", tags=["Airline Master"])
api_router.include_router(build_master_router(UnitOfMeasure, UnitOfMeasureCreate, UnitOfMeasureUpdate, UnitOfMeasureRead), prefix="/units-of-measure", tags=["Unit of Measure Master"])
api_router.include_router(build_master_router(HSCode, HSCodeCreate, HSCodeUpdate, HSCodeRead), prefix="/hs-codes", tags=["HS Code Master"])
api_router.include_router(build_master_router(ServiceType, ServiceTypeCreate, ServiceTypeUpdate, ServiceTypeRead), prefix="/service-types", tags=["Service Type Master"])
api_router.include_router(build_master_router(LeadSourceMaster, LeadSourceMasterCreate, LeadSourceMasterUpdate, LeadSourceMasterRead), prefix="/lead-sources", tags=["Lead Source Master"])
api_router.include_router(build_master_router(IndustryType, IndustryTypeCreate, IndustryTypeUpdate, IndustryTypeRead), prefix="/industry-types", tags=["Industry Type Master"])
api_router.include_router(build_master_router(DocumentType, DocumentTypeCreate, DocumentTypeUpdate, DocumentTypeRead), prefix="/document-types", tags=["Document Type Master"])
api_router.include_router(build_master_router(QuoteTncTemplate, QuoteTncTemplateCreate, QuoteTncTemplateUpdate, QuoteTncTemplateRead), prefix="/quote-tnc-templates", tags=["Quote T&C Template Master"])

api_router.include_router(account.router, prefix="/accounts", tags=["Accounts"])
api_router.include_router(contact.router, prefix="/contacts", tags=["Contacts"])
api_router.include_router(lead.router, prefix="/leads", tags=["Leads"])
api_router.include_router(opportunity.router, prefix="/opportunities", tags=["Opportunities"])
api_router.include_router(quotation.router, prefix="/quotations", tags=["Quotations"])
api_router.include_router(activity.router, prefix="/activities", tags=["Activities"])
api_router.include_router(role.router, prefix="/roles", tags=["Role Management"])
