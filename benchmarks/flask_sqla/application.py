#!/usr/bin/env python3
import json

from sqlalchemy import text

from flask import Flask, jsonify
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://asterisk:asterisk@172.17.0.2/benchmarks'
db = SQLAlchemy(app)

@app.route('/index')
def index():
    return jsonify({'hello': 'world'})

@app.route('/agents_with_pool')
def agents_with_pool():
    query = """
            SELECT
                af.number AS number,
                als.extension AS extension,
                als.context AS context,
                als.state_interface AS state_interface,
                'offline' AS status,
                '-1' AS extension_status,
                '0' AS paused
            FROM
                public.agentfeatures af
                LEFT JOIN public.agent_login_status als ON (af.id = als.agent_id)
            """
    sql = text(query)
    results = db.engine.execute(sql)
    output = []
    for row in results:
        output.append(list(row))
    return jsonify({'results': output})

@app.route('/agents_with_orm')
def agents_with_orm():
    db.reflect(app=app)

    class AgentFeatures(db.Model):
        __tablename__ = 'agentfeatures'

    class AgentLoginStatus(db.Model):
        __tablename__ = 'agent_login_status'

    results = db.session \
                .query(AgentFeatures.number,
                       AgentLoginStatus.extension,
                       AgentLoginStatus.context,
                       AgentLoginStatus.state_interface) \
                .outerjoin(AgentLoginStatus, AgentFeatures.id==AgentLoginStatus.agent_id) \
                .all()
    output = []
    for result in results:
        output.append(list(result))
    return jsonify({'results': output})

if __name__ == '__main__':
    app.run(debug=False)