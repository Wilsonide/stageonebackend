import hashlib
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.params import Query
from sqlalchemy import Boolean, Integer, String, cast, or_
from sqlalchemy.orm import Session

import models
from db import StringRecord, get_db
from helper import analyze_string, parse_natural_query, parse_query

router = APIRouter()


""" @router.get("/strings", response_model=list[UserRead])
def get_users(service: Annotated[Session, Depends(get_db)]):
    return service.list_users() """


@router.post("/strings", response_model=models.StringResponse)
def create_user(credential: models.StringData, db: Annotated[Session, Depends(get_db)]):
    if not credential.value:
        raise HTTPException(
            status_code=400, detail='Invalid request body or missing "value" field'
        )
    if not credential.value.strip():
        raise HTTPException(
            status_code=400, detail='Invalid request body or missing "value" field'
        )
    existing = (
        db.query(StringRecord).filter(StringRecord.value == credential.value).first()
    )
    if existing:
        raise HTTPException(
            status_code=409, detail="String already exists in the system"
        )
    sha256_hash = hashlib.sha256(credential.value.encode("utf-8")).hexdigest()
    properties = analyze_string(credential.value)
    new_string = StringRecord(
        id=sha256_hash,
        value=credential.value,
        properties=properties,
    )
    db.add(new_string)
    db.commit()
    db.refresh(new_string)
    print(new_string)
    return new_string


@router.get("/strings", response_model=models.DataFilterResponse)
def get_strings(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
):
    parsed_filters = parse_query(request.url.query)
    print(f"Filters applied1: {parsed_filters}")
    query = db.query(StringRecord)

    or_conditions = []
    for key, value in parsed_filters.items():
        prop = StringRecord.properties[key].cast(String)

        if isinstance(value, bool):
            or_conditions.append(cast(prop, Boolean) == value)
        elif isinstance(value, int):
            or_conditions.append(cast(prop, Integer) == value)
        else:
            or_conditions.append(prop == str(value))

        query = query.filter(or_(*or_conditions))

    results = query.all()
    data = [
        {
            "id": item.id,
            "value": item.value,
            "properties": {
                "length": item.properties["length"],
                "is_palindrome": item.properties["is_palindrome"],
                "word_count": item.properties["word_count"],
                "unique_characters": item.properties["unique_characters"],
                "sha256_hash": item.properties["sha256_hash"],
                "character_frequency_map": item.properties["character_frequency_map"],
            },
            "created_at": item.created_at,
        }
        for item in results
    ]

    print(f"Filters applied: {parsed_filters}")

    return {
        "data": data,
        "count": len(data),
        "filters_applied": parsed_filters,
    }


@router.get(
    "/strings/filter-by-natural-language", response_model=models.NaturalFilterResponse
)
def get_strings_n(
    db: Annotated[Session, Depends(get_db)],
    query: str = Query(default=None, description="Natural language query string"),
):
    print(query)
    filters = parse_natural_query(query)
    print(f"Filters applied: {filters}")

    q = db.query(StringRecord)

    # Apply filters as OR conditions
    if filters:
        or_conditions = []
        for key, value in filters.items():
            prop = StringRecord.properties[key].cast(String)

            if isinstance(value, bool):
                or_conditions.append(cast(prop, Boolean) == value)
            elif isinstance(value, int):
                or_conditions.append(cast(prop, Integer) == value)
            else:
                or_conditions.append(prop == str(value))

        q = q.filter(or_(*or_conditions))

    results = q.all()

    data = [
        {
            "id": item.id,
            "value": item.value,
            "properties": {
                "length": item.properties["length"],
                "is_palindrome": item.properties["is_palindrome"],
                "word_count": item.properties["word_count"],
                "unique_characters": item.properties["unique_characters"],
                "sha256_hash": item.properties["sha256_hash"],
                "character_frequency_map": item.properties["character_frequency_map"],
            },
            "created_at": item.created_at,
        }
        for item in results
    ]

    return {
        "data": data,
        "count": len(data),
        "interpreted_query": {
            "original": str(query),
            "parsed_filters": filters,
        },
    }


@router.get("/strings/{string_value}", response_model=models.StringResponse)
def get_string(
    string_value: str,
    db: Annotated[Session, Depends(get_db)],
):
    data = db.query(StringRecord).filter(StringRecord.value == string_value).first()
    if not data:
        raise HTTPException(
            status_code=404, detail="String does not exist in the system"
        )
    return data


@router.delete("/strings/{string_value}", status_code=204)
def delete_string(string_value: str, db: Annotated[Session, Depends(get_db)]):
    record = db.query(StringRecord).filter(StringRecord.value == string_value).first()
    if not record:
        raise HTTPException(
            status_code=404, detail=" String does not exist in the system"
        )
    db.delete(record)
    db.commit()
