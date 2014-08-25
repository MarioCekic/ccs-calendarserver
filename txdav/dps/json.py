##
# Copyright (c) 2014 Apple Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
##

from __future__ import absolute_import

"""
JSON serialization utilities.
"""

__all__ = [
    "expressionAsJSON",
    "expressionAsJSONText",
    "expressionFromJSON",
    "expressionFromJSONText",
]

from json import dumps, loads as from_json_text

from twext.who.expression import (
    CompoundExpression, Operand,
    MatchExpression, MatchType, MatchFlags,
    ExistsExpression, BooleanExpression
)



def matchExpressionAsJSON(expression):
    return dict(
        type=expression.__class__.__name__,
        field=expression.fieldName.name,
        value=expression.fieldValue,
        match=expression.matchType.name,
        flags=expression.flags.name,
    )



def existsExpressionAsJSON(expression):
    return dict(
        type=expression.__class__.__name__,
        field=expression.fieldName.name,
    )



def booleanExpressionAsJSON(expression):
    return dict(
        type=expression.__class__.__name__,
        field=expression.fieldName.name,
    )



def compoundExpressionAsJSON(expression):
    return dict(
        type=expression.__class__.__name__,
        operand=expression.operand.name,
        expressions=[expressionAsJSON(e) for e in expression.expressions],
    )



def expressionAsJSON(expression):
    if isinstance(expression, CompoundExpression):
        return compoundExpressionAsJSON(expression)

    if isinstance(expression, MatchExpression):
        return matchExpressionAsJSON(expression)

    if isinstance(expression, ExistsExpression):
        return existsExpressionAsJSON(expression)

    if isinstance(expression, BooleanExpression):
        return booleanExpressionAsJSON(expression)

    raise TypeError(
        "Unknown expression type: {!r}".format(expression)
    )



def expressionAsJSONText(expression):
    json = expressionAsJSON(expression)
    return to_json_text(json)



def matchTypeFromJSON(json):
    return MatchType.lookupByName(json)



def matchFlagsFromJSON(json):
    if json == "{}":
        return MatchFlags.none

    if json.startswith("{") and json.endswith("}"):
        # Composite flags: "{A,B,C,...}"
        flags = MatchFlags.none
        for flag in json[1:-1].split(","):
            flags |= MatchFlags.lookupByName(flag)

        return flags

    return MatchFlags.lookupByName(json)



def matchExpressionFromJSON(service, json):
    try:
        jsonField = json["field"]
        jsonValue = json["value"]
    except KeyError as e:
        raise ValueError(
            "JSON match expression must have {!r} key.".format(e[0])
        )

    fieldName = service.fieldName.lookupByName(jsonField)
    fieldValue = unicode(jsonValue)
    matchType = matchTypeFromJSON(json.get("match", "equals"))
    flags = matchFlagsFromJSON(json.get("flags", "{}"))

    return MatchExpression(
        fieldName, fieldValue,
        matchType=matchType, flags=flags,
    )



def existsExpressionFromJSON(service, json):
    try:
        jsonField = json["field"]
    except KeyError as e:
        raise ValueError(
            "JSON match expression must have {!r} key.".format(e[0])
        )

    fieldName = service.fieldName.lookupByName(jsonField)

    return ExistsExpression(fieldName)



def booleanExpressionFromJSON(service, json):
    try:
        jsonField = json["field"]
    except KeyError as e:
        raise ValueError(
            "JSON match expression must have {!r} key.".format(e[0])
        )

    fieldName = service.fieldName.lookupByName(jsonField)

    return BooleanExpression(fieldName)



def compoundExpressionFromJSON(json):
    try:
        expressions_json = json["expressions"]
        operand_json = json["operand"]
    except KeyError as e:
        raise ValueError(
            "JSON compound expression must have {!r} key.".format(e[0])
        )

    expressions = tuple(expressionFromJSON(e) for e in expressions_json)
    operand = Operand.lookupByName(operand_json)

    return CompoundExpression(expressions, operand)



def expressionFromJSON(json):
    if not isinstance(json, dict):
        raise TypeError("JSON expression must be a dict.")

    try:
        json_type = json["type"]
    except KeyError as e:
        raise ValueError("JSON expression must have {!r} key.".format(e[0]))

    if json_type == "CompoundExpression":
        return compoundExpressionFromJSON(json)

    if json_type == "MatchExpression":
        return matchExpressionFromJSON(json)

    if json_type == "ExistsExpression":
        return existsExpressionFromJSON(json)

    if json_type == "BooleanExpression":
        return booleanExpressionFromJSON(json)

    raise NotImplementedError(
        "Unknown expression type: {}".format(json_type)
    )



def expressionFromJSONText(jsonText):
    json = from_json_text(jsonText)
    return expressionFromJSON(json)



def to_json_text(obj):
    """
    Convert an object into JSON text.

    @param obj: An object that is serializable to JSON.
    @type obj: L{object}

    @return: JSON text.
    @rtype: L{unicode}
    """
    return dumps(obj, separators=(',', ':')).decode("UTF-8")
