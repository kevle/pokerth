/*****************************************************************************
 * PokerTH - The open source texas holdem engine                             *
 * Copyright (C) 2006-2012 Felix Hammer, Florian Thauer, Lothar May          *
 *                                                                           *
 * This program is free software: you can redistribute it and/or modify      *
 * it under the terms of the GNU Affero General Public License as            *
 * published by the Free Software Foundation, either version 3 of the        *
 * License, or (at your option) any later version.                           *
 *****************************************************************************/

#ifdef __EMSCRIPTEN__

#include <net/clientwssendbuffer.h>
#include <net/netpacket.h>

ClientWsSendBuffer::ClientWsSendBuffer(QWebSocket *ws)
	: m_ws(ws)
{
}

void
ClientWsSendBuffer::AsyncSendNextPacket(boost::shared_ptr<SessionData> /*session*/)
{
	// Nothing to do: InternalStorePacket sends synchronously via QWebSocket.
}

void
ClientWsSendBuffer::InternalStorePacket(boost::shared_ptr<SessionData> /*session*/,
                                         boost::shared_ptr<NetPacket> packet)
{
	// The PokerTH WebSocket server (WebReceiveBuffer) expects each message to
	// contain raw protobuf bytes with NO 4-byte length header.
	uint32_t sz = static_cast<uint32_t>(packet->GetMsg()->ByteSizeLong());
	QByteArray buf(static_cast<int>(sz), '\0');
	packet->GetMsg()->SerializeWithCachedSizesToArray(
		reinterpret_cast<google::protobuf::uint8 *>(buf.data()));
	m_ws->sendBinaryMessage(buf);
}

#endif // __EMSCRIPTEN__
