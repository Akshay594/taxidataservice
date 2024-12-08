# src/api/graphql/schema.py

import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from src.db.models import TaxiTrip, TripAggregation
from datetime import datetime

class TripType(SQLAlchemyObjectType):
    class Meta:
        model = TaxiTrip
        interfaces = (graphene.relay.Node,)

class TripAggregationType(SQLAlchemyObjectType):
    class Meta:
        model = TripAggregation

class Query(graphene.ObjectType):
    trip = graphene.Field(
        TripType,
        id=graphene.Int(required=True),
        description="Get a specific trip by ID"
    )
    
    trips = graphene.List(
        TripType,
        start_date=graphene.DateTime(),
        end_date=graphene.DateTime(),
        limit=graphene.Int(default_value=100),
        description="Get trips within a date range"
    )
    
    daily_stats = graphene.Field(
        TripAggregationType,
        date=graphene.Date(required=True),
        description="Get daily trip statistics"
    )
    
    def resolve_trip(self, info, id):
        return info.context["session"].query(TaxiTrip).filter(TaxiTrip.id == id).first()
    
    def resolve_trips(self, info, start_date=None, end_date=None, limit=100):
        query = info.context["session"].query(TaxiTrip)
        
        if start_date:
            query = query.filter(TaxiTrip.pickup_datetime >= start_date)
        if end_date:
            query = query.filter(TaxiTrip.pickup_datetime <= end_date)
            
        return query.limit(limit).all()
    
    def resolve_daily_stats(self, info, date):
        return info.context["session"].query(TripAggregation)\
            .filter(TripAggregation.date == date).first()

schema = graphene.Schema(query=Query)