// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract CertificateVerifier {
    struct Certificate {
        string participantName;
        string participantEmail;
        string seminarTitle;
        string seminarDate;
        bytes signature;
        address issuer;
        string issuerName;
        uint256 timestamp;
        bool isValid;
    }
    
    // Mapping untuk menyimpan sertifikat berdasarkan ID
    mapping(string => Certificate) private certificates;
    
    // Mapping untuk menyimpan hash sertifikat
    mapping(string => string) private certificateHashes;
    
    // Event yang dipancarkan saat sertifikat diterbitkan
    event CertificateIssued(
        string certificateId,
        string participantName,
        string seminarTitle,
        address issuer,
        string issuerName
    );
    
    // Event yang dipancarkan saat hash disimpan
    event HashStored(
        string certificateId,
        string certificateHash
    );
    
    // Fungsi untuk menerbitkan sertifikat
    function issueCertificate(
        string memory _certificateId,
        string memory _participantName,
        string memory _participantEmail,
        string memory _seminarTitle,
        string memory _seminarDate,
        bytes memory _signature,
        string memory _issuerName
    ) public {
        require(bytes(_certificateId).length > 0, "Certificate ID cannot be empty");
        require(bytes(_participantName).length > 0, "Participant name cannot be empty");
        require(bytes(_seminarTitle).length > 0, "Seminar title cannot be empty");
        require(bytes(_issuerName).length > 0, "Issuer name cannot be empty");
        require(!certificates[_certificateId].isValid, "Certificate already exists");
        
        certificates[_certificateId] = Certificate({
            participantName: _participantName,
            participantEmail: _participantEmail,
            seminarTitle: _seminarTitle,
            seminarDate: _seminarDate,
            signature: _signature,
            issuer: msg.sender,
            issuerName: _issuerName,
            timestamp: block.timestamp,
            isValid: true
        });
        
        emit CertificateIssued(_certificateId, _participantName, _seminarTitle, msg.sender, _issuerName);
    }
    
    // Fungsi untuk menyimpan hash sertifikat
    function storeCertificateHash(
        string memory _certificateId,
        string memory _certificateHash
    ) public {
        require(bytes(_certificateId).length > 0, "Certificate ID cannot be empty");
        require(bytes(_certificateHash).length > 0, "Certificate hash cannot be empty");
        require(certificates[_certificateId].isValid, "Certificate must exist first");
        require(certificates[_certificateId].issuer == msg.sender, "Only issuer can store hash");
        
        certificateHashes[_certificateId] = _certificateHash;
        
        emit HashStored(_certificateId, _certificateHash);
    }
    
    // Fungsi untuk mendapatkan hash sertifikat
    function getCertificateHash(string memory _certificateId) public view returns (string memory) {
        return certificateHashes[_certificateId];
    }
    
    // Fungsi untuk memverifikasi sertifikat
    function verifyCertificate(string memory _certificateId) public view returns (
        string memory participantName,
        string memory participantEmail,
        string memory seminarTitle,
        string memory seminarDate,
        bytes memory signature,
        string memory issuerName,
        uint256 timestamp,
        bool isValid
    ) {
        Certificate memory cert = certificates[_certificateId];
        return (
            cert.participantName,
            cert.participantEmail,
            cert.seminarTitle,
            cert.seminarDate,
            cert.signature,
            cert.issuerName,
            cert.timestamp,
            cert.isValid
        );
    }
    
    // Fungsi untuk memvalidasi signature
    function validateSignature(
        string memory _certificateId,
        string memory _participantName,
        string memory _seminarTitle,
        bytes memory _signature,
        string memory _issuerName
    ) public view returns (bool) {
        Certificate memory cert = certificates[_certificateId];
        
        // Periksa apakah sertifikat ada dan valid
        if (!cert.isValid) {
            return false;
        }
        
        // Periksa apakah data cocok
        if (keccak256(abi.encodePacked(cert.participantName)) != keccak256(abi.encodePacked(_participantName)) ||
            keccak256(abi.encodePacked(cert.seminarTitle)) != keccak256(abi.encodePacked(_seminarTitle)) ||
            keccak256(abi.encodePacked(cert.issuerName)) != keccak256(abi.encodePacked(_issuerName))) {
            return false;
        }
        
        // Periksa signature
        if (keccak256(cert.signature) != keccak256(_signature)) {
            return false;
        }
        
        return true;
    }
    
    // Fungsi untuk membatalkan sertifikat (hanya issuer yang bisa)
    function revokeCertificate(string memory _certificateId) public {
        require(certificates[_certificateId].isValid, "Certificate does not exist or already revoked");
        require(certificates[_certificateId].issuer == msg.sender, "Only issuer can revoke certificate");
        
        certificates[_certificateId].isValid = false;
    }
    
    // Fungsi untuk memeriksa apakah sertifikat ada
    function certificateExists(string memory _certificateId) public view returns (bool) {
        return bytes(certificates[_certificateId].participantName).length > 0;
    }
    
    // Fungsi untuk mendapatkan jumlah sertifikat yang diterbitkan oleh alamat tertentu
    function getCertificatesByIssuer(address _issuer) public view returns (uint256 count) {
        // Note: Implementasi ini memerlukan array tambahan untuk tracking
        // Untuk saat ini, return 0 sebagai placeholder
        return 0;
    }
}