# -*- coding: utf-8 -*-

from odoo import models, fields

class TallerMarca(models.Model):
    _name = 'taller.vehiculos.marca'
    _rec_name = "marca"

    marca = fields.Char('Marca')

class TallerModelo(models.Model):
    _name = 'taller.vehiculos.modelo'
    _rec_name = "modelo"

    modelo = fields.Char('Modelo')
    marca = fields.Many2one("taller.vehiculos.marca",'Marca')

class TallerVehiculos(models.Model):
    _name = 'taller.vehiculos'
    
    name = fields.Char("Nombre", required=1)
    partner_id = fields.Many2one("res.partner",'Cliente', domain="[('customer', '=', True)]")
    modelo = fields.Many2one("taller.vehiculos.modelo",'Modelo')
    marca = fields.Many2one("taller.vehiculos.marca",'Marca')
    numero_de_serie = fields.Char("Numero de serie")
    placas = fields.Char("Placas")
    serie_de_motor = fields.Char("Serie del motor")
    cantidad_horas = fields.Char("Cantidad de horas")